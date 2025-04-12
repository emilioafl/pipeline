from abc import abstractmethod

from pipeline.common.jobs import PipelineJob
from pipeline.common.environment import PipelineJobEnvironment

class BaseScannerEnvironment(PipelineJobEnvironment):
    def __init__(self):
        super().__init__()
        # Aquí se pueden definir variables de entorno específicas para el escáner

class BaseScanner(PipelineJob):
    
    environment: BaseScannerEnvironment
    
    @abstractmethod
    def run_analysis(self):
        pass

    @abstractmethod
    def make_report(self):
        pass

    def post_execute(self) -> None:
        self.make_report()