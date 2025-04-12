from os import getenv
from os.path import exists

import pipeline.exceptions as exc
from pipeline.common.tools import CommandTools
from pipeline.common.gitlab import PredefinedVariables
from pipeline.scanning.base import BaseScanner, BaseScannerEnvironment

class SonarQubeEnvironment(BaseScannerEnvironment):
    def __init__(self):
        super().__init__()
        self.SONAR_PROPERTIES_PATH: str = getenv("SONAR_PROPERTIES_PATH", "")
        self.SONAR_PROJECT_KEY: str = getenv("SONAR_PROJECT_KEY", "")
        self.SONAR_HOST_URL: str = getenv("SONAR_HOST_URL", "")
        self.SONAR_TOKEN: str = getenv("SONAR_TOKEN", "")
        self.SONAR_ORGANIZATION: str = getenv("SONAR_ORGANIZATION", "")
        self.SONAR_EXECUTION_ERROR_MSG: str = "ERROR Error during SonarScanner Engine execution"

class SonarQube(BaseScanner):
    
    environment: SonarQubeEnvironment
    
    def _load_config(self):
        super()._load_config()
        self.environment = SonarQubeEnvironment()
        super()._check_environment()
    
    def execute(self) -> None:
        self.printer.info("Iniciando SonarQube...")
        result = self.run_analysis()
        output = f"{result.stdout}\n--------\n{result.stderr}"
        self.logger.info(output)
        if result.stderr and self.environment.SONAR_EXECUTION_ERROR_MSG in result.stderr:
            self.logger.critical(output)
            raise exc.ExitError(
                code=1,
                force_exit=True,
                critical=True,
                user_message="Fatal: El análisis de SonarQube no se completó correctamente."
            )
        if result.returncode == 0:
            self.printer.success("¡Sus cambios han pasado el Quality Gate de " \
                                 "SonarQube exitosamente!")
            self.logger.info("SonarQube did not find any errors.")
            return
        
        self.printer.failure("Sus cambios no pasaron el Quality Gate de SonarQube.")
        self.logger.info("SonarQube found errors.")
        self.logger.info("Failing job...")
        raise exc.ExitError(1, user_message=None, user_hint=None)

    def run_analysis(self):
        sonar_scanner_opts = [
            f"sonar.projectKey={self.environment.SONAR_PROJECT_KEY}",
            f"sonar.projectName={PredefinedVariables.CI_PROJECT_NAME}",
            "sonar.qualitygate.wait=true",
            f"sonar.projectBaseDir={PredefinedVariables.CI_PROJECT_DIR}",
            f"sonar.organization={self.environment.SONAR_ORGANIZATION}"
        ]
        if exists(self.environment.SONAR_PROPERTIES_PATH):
            sonar_scanner_opts.append(f"project.settings={self.environment.SONAR_PROPERTIES_PATH}")

        sonar_scanner_opts = (f"-D{opt}" for opt in sonar_scanner_opts)
        sonar_scanner_command = ["sonar-scanner"]
        sonar_scanner_command.extend(sonar_scanner_opts)
        result = CommandTools.run_command(
            command=" ".join(sonar_scanner_command),
            workdir=PredefinedVariables.CI_PROJECT_DIR
        )
        return result

    def make_report(self):
        analysis_url = f"{self.environment.SONAR_HOST_URL}/dashboard" \
                       f"?id={self.environment.SONAR_PROJECT_KEY}&branch={PredefinedVariables.CI_COMMIT_REF_NAME}&resolved=false"
        self.printer.hint(f"Puede revisar los resultados del último análisis en el " \
            f"siguiente enlace: {analysis_url}", crop=False, overflow="ignore")