import pipeline.exceptions as exc

from pipeline.build.base import BaseBuilder
from pipeline.common.tools import CommandTools
from pipeline.common.gitlab import PredefinedVariables

class MavenBuilder(BaseBuilder):
    def execute(self):
        self.printer.info("Compilando el proyecto con Maven...")
        result = CommandTools.run_command(
            "mvn clean package -DskipTests=true",
            workdir=PredefinedVariables.CI_PROJECT_DIR
        )
        self.logger.info(f"{result.stdout}\n\n{result.stderr}")
        if result.returncode != 0:
            raise exc.ExitError(
                user_message="Error al compilar el proyecto con Maven",
                log_message="Maven compilation failed."
            )
        self.printer.success("Compilación de Maven completada con éxito.")