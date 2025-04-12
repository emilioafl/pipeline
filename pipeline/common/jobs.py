from logging import Logger
from abc import ABC, abstractmethod
from typing import Type
from gitlab import Gitlab
from gitlab.v4.objects import Project, ProjectMergeRequest

import pipeline.exceptions as exc
from pipeline import logger
from pipeline.common.environment import PipelineJobEnvironment
from pipeline.common.gitlab import PredefinedVariables
from pipeline.common.printer import Printer

class PipelineJob(ABC):
    """
    Pipeline Jobs base class.
    """
    logger: Logger
    gitlab_object: Gitlab
    project_object: Project
    utilities_project: Project | None
    merge_request_object: ProjectMergeRequest | None
    environment: PipelineJobEnvironment
    printer: Printer
    non_mandatory_env_vars: list[str] = ["SSL_VERIFY"]
    failed: bool

    @exc.catch_errors
    def __init__(self) -> None:
        self._load_config()

    def _load_config(self) -> None:
        self.failed = False
        self.tool = self.__class__.__name__
        self.logger = logger
        self.environment = PipelineJobEnvironment()
        self.printer = Printer()
        if not self.environment.SSL_VERIFY:
            from urllib3 import disable_warnings
            disable_warnings()
        self.gitlab_object = Gitlab(
            url=PredefinedVariables.CI_SERVER_URL,
            private_token=PredefinedVariables.GITLAB_PRIVATE_TOKEN,
            ssl_verify=self.environment.SSL_VERIFY
        )
        self.project_object = self.gitlab_object.projects.get(
            id=PredefinedVariables.CI_PROJECT_ID
        )
        self.logger.info(f"Loaded configuration for {self.__class__.__name__}.")
    
    def _check_environment(self) -> None:
        error = False
        for var in dir(self.environment):
            if var.startswith("__"):  # Skip built-in methods
                continue
            value = getattr(self.environment, var)
            if value == "" and var not in self.non_mandatory_env_vars:
                error = True
                self.printer.failure(f"La variable de entorno {var} no está definida.")
        if error:
            raise exc.ExitError(
                code=1,
                force_exit=True,
                critical=True,
                log_message=f"Environment variable {var} is not defined."
            )

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def post_execute(self) -> None:
        pass

    def run(self) -> None:
        try:
            self.execute()
            self.post_execute()
        except exc.ExitError as e:
            self.failed = True
            if not e.force_exit:
                self.post_execute()
            raise
    
class PipelineJobDispatcher:
    def __init__(self):
        self._jobs: dict[str, Type[PipelineJob]] = {}

    def register_job(self, job_name: str, job_cls: Type[PipelineJob]) -> None:
        self._jobs[job_name] = job_cls

    @exc.catch_errors
    def dispatch(self, job_name: str) -> None:
        job = self._jobs.get(job_name)
        if job is None:
            raise exc.JobNotFoundError(f"No se encontró el job {job_name}.")
        job = job()
        job.run()