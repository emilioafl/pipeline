from pipeline.common.jobs import PipelineJobDispatcher
from pipeline.common.gitlab import PredefinedVariables
from pipeline.build.maven import MavenBuilder
from pipeline.scanning.unit_tests import UnitTests
from pipeline.scanning.sonarqube import SonarQube
from pipeline.scanning.code_coverage import CodeCoverage
from pipeline.images.create_image import CreateImage
from pipeline.scanning.grype import Grype
from pipeline.deploy.kubernetes import KubernetesManager

class Pipeline:
    def __init__(self):
        self.dispatcher = PipelineJobDispatcher()
        self._register_jobs()
        self._run()

    def _register_jobs(self):
        self.dispatcher.register_job("build", MavenBuilder)
        self.dispatcher.register_job("unit-tests", UnitTests)
        self.dispatcher.register_job("sonarqube", SonarQube)
        self.dispatcher.register_job("code-coverage", CodeCoverage)
        self.dispatcher.register_job("create-image", CreateImage)
        self.dispatcher.register_job("grype", Grype)
        self.dispatcher.register_job("kubernetes", KubernetesManager)

    def _run(self):
        self.dispatcher.dispatch(PredefinedVariables.JOB_IDENTIFIER)

if __name__ == "__main__":
    pipeline = Pipeline()