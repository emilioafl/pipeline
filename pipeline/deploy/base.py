from abc import abstractmethod

from pipeline.common.jobs import PipelineJob
from pipeline.common.environment import PipelineJobEnvironment

class BaseDeployEnvironment(PipelineJobEnvironment):
    def __init__(self):
        super().__init__()
        # Aquí se pueden definir variables de entorno específicas para el despliegue

class DeployManager(PipelineJob):
    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def check_health(self) -> bool:
        pass

    def post_execute(self):
        pass