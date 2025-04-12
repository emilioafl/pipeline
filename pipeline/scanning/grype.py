from os.path import exists
from json import loads

import pipeline.exceptions as exc

from pipeline.common.gitlab import PredefinedVariables
from pipeline.common.tools import DockerTools, CommandTools
from pipeline.scanning.base import BaseScanner, BaseScannerEnvironment

class GrypeEnvironment(BaseScannerEnvironment):
    def __init__(self):
        super().__init__()
        self.JSON_LOG_FILE: str = f"{PredefinedVariables.CI_PROJECT_DIR}/docker-image-scan-log.json"
        self.HTML_REPORT_FILE: str = f"{PredefinedVariables.CI_PROJECT_DIR}/docker-image-scan-result.html"
        self.HTML_TEMPLATE: str = f"{self.TEMPLATES_DIR}/grype-template.tmpl"
        self.IMAGE_NAME: str = f"{PredefinedVariables.CI_REGISTRY}/{PredefinedVariables.CI_PROJECT_PATH}:{PredefinedVariables.CI_COMMIT_REF_NAME}"

class Grype(BaseScanner):
    
    environment: GrypeEnvironment

    def _load_config(self):
        super()._load_config()
        self.environment = GrypeEnvironment()
        super()._check_environment()

    def execute(self) -> None:
        self.setup_analysis()
        self.run_analysis()
        errors = self.analyze_results()
        if errors:
            raise exc.ExitError(
                code=1,
                user_message="El análisis de vulnerabilidades encontró novedades que deben ser atendidas.",
                log_message="Vulnerabilities found during analysis."
            )
        self.printer.success("Análisis de vulnerabilidades completado sin novedades.")

    def setup_analysis(self):
        self.printer.info("Construyendo imagen Docker...")
        DockerTools.login_to_docker_registry(
            registry=PredefinedVariables.CI_REGISTRY,
            username=PredefinedVariables.CI_REGISTRY_USER,
            password=PredefinedVariables.CI_REGISTRY_PASSWORD
        )
        result = DockerTools.build_docker_image(
            name=self.environment.IMAGE_NAME.split(":")[0],
            tag=self.environment.IMAGE_NAME.split(":")[1],
            no_cache=True,
            context=PredefinedVariables.CI_PROJECT_DIR
        )
        if result.returncode != 0:
            raise exc.ExitError(
                code=1,
                force_exit=True,
                user_message="Error al construir la imagen Docker.",
                log_message=f"Docker build failed with return code: {result.returncode}. STDOUT/STDERR: {result.stdout}\n\n{result.stderr}"
            )
        self.printer.success("Imagen Docker construida exitosamente.")

    def run_analysis(self):
        self.printer.info("Ejecutando análisis de vulnerabilidades...")
        command = f'grype {self.environment.IMAGE_NAME} ' \
                    f'--only-fixed ' \
                    f'--exclude /app ' \
                    f'-o json > {self.environment.JSON_LOG_FILE}'
        result = CommandTools.run_command(
            command=command,
            shell=True,
            split_cmd=False
        )
        if result.returncode != 0:
            raise exc.ExitError(
                code=1,
                force_exit=True,
                critical=True,
                user_message="Error al ejecutar el comando grype.",
                log_message=f"Grype command failed: {result.stdout}\n\n{result.stderr}"
            )
        self.logger.info(f"Grype command output: {result.stdout}\n\n{result.stderr}")
        self.printer.success("Análisis de vulnerabilidades completado exitosamente.")

    def analyze_results(self) -> bool:
        self.printer.info("Analizando los resultados...")
        if not exists(self.environment.JSON_LOG_FILE):
            raise exc.ExitError(
                code=1,
                force_exit=True,
                critical=True,
                user_message="No se encontró el archivo de log JSON.",
                log_message="JSON log file not found."
            )
        with open(self.environment.JSON_LOG_FILE, "r") as file:
            data = loads(file.read())
            valid_vulnerabilities = [vuln for vuln in data["matches"]
                                        if vuln["vulnerability"]["severity"] != "Unknown"]
            if len(valid_vulnerabilities) == 0:
                self.printer.success("¡No se encontraron vulnerabilidades!")
                return
            total_critical_vuln = len([vuln for vuln in valid_vulnerabilities
                                        if vuln["vulnerability"]["severity"] == "Critical"])
            total_high_vuln = len([vuln for vuln in valid_vulnerabilities
                                    if vuln["vulnerability"]["severity"] == "High"])
            total_medium_vuln = len([vuln for vuln in valid_vulnerabilities
                                        if vuln["vulnerability"]["severity"] == "Medium"])
            total_low_vuln = len([vuln for vuln in valid_vulnerabilities
                                    if vuln["vulnerability"]["severity"] == "Low"])
            if total_critical_vuln:
                self.printer.failure(f"Se han encontrado {total_critical_vuln} vulnerabilidades de severidad CRÍTICA.")
            if total_high_vuln:
                self.printer.failure(f"Se han encontrado {total_high_vuln} vulnerabilidades de severidad ALTA.")
            if total_medium_vuln:
                self.printer.failure(f"Se han encontrado {total_medium_vuln} vulnerabilidades de severidad MEDIA.")
            if total_low_vuln:
                self.printer.warning(f"Se han encontrado {total_low_vuln} vulnerabilidades de severidad BAJA.")
            return total_critical_vuln > 0 or total_high_vuln > 0 or total_medium_vuln > 0

    def make_report(self):
        self.run_grype_report_command()

    def run_grype_report_command(self):
        self.printer.info("Generando reporte...")
        command = f'grype docker:{self.environment.IMAGE_NAME} ' \
                    f'--only-fixed ' \
                    f'--exclude /app ' \
                    f'-o template ' \
                    f'-t {self.environment.HTML_TEMPLATE} > {self.environment.HTML_REPORT_FILE}'
        result = CommandTools.run_command(
            command=command,
            shell=True,
            split_cmd=False
        )
        if result.returncode != 0:
            raise exc.ExitError(
                code=1,
                force_exit=True,
                critical=True,
                user_message="Ha ocurrido un error al generar el reporte.",
                log_message=f"Grype command failed with return code: {result.stdout}\n\n{result.stderr}"
            )
        self.printer.success("Reporte generado exitosamente.")
    
    def post_execute(self) -> None:
        self.make_report()
