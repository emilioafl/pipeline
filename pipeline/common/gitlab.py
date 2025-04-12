from os import getenv
from gitlab.v4.objects import Project
from gitlab import GitlabGetError
from typing import Any
from base64 import b64decode

class PredefinedVariables:
    CI_SERVER_URL: str = getenv("CI_SERVER_URL", "")
    CI_DEFAULT_BRANCH: str = getenv("CI_DEFAULT_BRANCH", "")
    CI_PROJECT_DIR: str = getenv("CI_PROJECT_DIR", "")
    CI_PROJECT_NAME: str = getenv("CI_PROJECT_NAME", "")
    CI_PROJECT_ID: str = getenv("CI_PROJECT_ID", "")
    CI_PROJECT_NAMESPACE_ID: str = getenv("CI_PROJECT_NAMESPACE_ID", "")
    CI_PROJECT_NAMESPACE: str = getenv("CI_PROJECT_NAMESPACE", "")
    CI_PROJECT_ROOT_NAMESPACE: str = getenv("CI_PROJECT_ROOT_NAMESPACE", "")
    CI_PROJECT_PATH: str = getenv("CI_PROJECT_PATH", "")
    CI_REPOSITORY_URL: str = getenv("CI_REPOSITORY_URL", "")
    CI_COMMIT_MESSAGE: str = getenv("CI_COMMIT_MESSAGE", "")
    CI_COMMIT_AUTHOR: str = getenv("CI_COMMIT_AUTHOR", "")
    CI_COMMIT_BRANCH: str = getenv("CI_COMMIT_BRANCH", "")
    CI_COMMIT_SHA: str = getenv("CI_COMMIT_SHA", "")
    CI_COMMIT_SHORT_SHA: str = getenv("CI_COMMIT_SHORT_SHA", "")
    CI_COMMIT_REF_NAME: str = getenv("CI_COMMIT_REF_NAME", "")
    CI_COMMIT_TITLE: str = getenv("CI_COMMIT_TITLE", "")
    CI_JOB_NAME: str = getenv("CI_JOB_NAME", "")
    CI_JOB_ID: str = getenv("CI_JOB_ID", "")
    CI_JOB_URL: str = getenv("CI_JOB_URL", "")
    CI_JOB_STAGE: str = getenv("CI_JOB_STAGE", "")
    CI_JOB_IMAGE: str = getenv("CI_JOB_IMAGE", "")
    CI_PIPELINE_ID: str = getenv("CI_PIPELINE_ID", "")
    CI_PIPELINE_URL: str = getenv("CI_PIPELINE_URL", "")
    CI_REGISTRY: str = getenv("CI_REGISTRY", "")
    CI_REGISTRY_PASSWORD: str = getenv("CI_REGISTRY_PASSWORD", "")
    CI_REGISTRY_USER: str = getenv("CI_REGISTRY_USER", "")
    GITLAB_USER_ID: str = getenv("GITLAB_USER_ID", "")
    GITLAB_USER_EMAIL: str = getenv("GITLAB_USER_EMAIL", "")
    GITLAB_USER_NAME: str = getenv("GITLAB_USER_NAME", "")
    GITLAB_USER_LOGIN: str = getenv("GITLAB_USER_LOGIN", "")
    CI_MERGE_REQUEST_IID: str = getenv("CI_MERGE_REQUEST_IID", "")
    CI_MERGE_REQUEST_TARGET_BRANCH_NAME: str = getenv("CI_MERGE_REQUEST_TARGET_BRANCH_NAME", "")
    CI_MERGE_REQUEST_TITLE: str = getenv("CI_MERGE_REQUEST_TITLE", "")
    GITLAB_PRIVATE_TOKEN: str = getenv("GITLAB_PRIVATE_TOKEN", "")
    JOB_IDENTIFIER: str = getenv("JOB_IDENTIFIER", "")

class Utils:
    @staticmethod
    def set_project_cicd_variable(
        project_obj: Project,
        variable_name: str,
        new_value: str
    ):
        """
        Sets the value of a project's CI/CD variable. If the variable doesn't exist,
        it will be created.

        :param gitlab.v4.objects.Project project_obj: The GitLab Project object that will be used.
        :param str variable_name: The name of the variable to be updated.
        :param str new_value: The new value of the given variable.

        :raises GitlabCreateError: If the server cannot create the variable.
        :raises GitlabUpdateError: If the server cannot update the variable.
        """
        try:
            variable = project_obj.variables.get(variable_name)
        except GitlabGetError:
            project_obj.variables.create({
                "key": variable_name,
                "value": new_value
            })
            return
        variable.value = new_value
        variable.save()
    
    @staticmethod
    def get_file_from_project(
        file_path: str,
        project_object: Project,
        ref: str = "master",
        **kwargs: Any
    ) -> str:
        """
        Gets a file from the given project id.

        :param str file_path: The file path in the GitLab Project.
        :param gitlab.v4.objects.Project project_obj: The GitLab Project object that will be used to retrieve the file.
        :param str ref: The ref that will be used to retrieve the file.

        :returns:
            The file's content.
        
        :raises GitlabGetError: If the given file could not be found.
        """
        file = project_object.files.get(
            file_path=file_path,
            ref=ref,
            **kwargs
        )
        file = b64decode(file.content).decode()
        return file
