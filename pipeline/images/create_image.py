import pipeline.exceptions as exc

from pipeline.common.jobs import PipelineJob
from pipeline.common.environment import PipelineJobEnvironment
from pipeline.common.tools import DockerTools
from pipeline.common.gitlab import PredefinedVariables

class CreateImageEnvironment(PipelineJobEnvironment):
    def __init__(self):
        super().__init__()
        # Aquí se pueden definir variables de entorno específicas para 
        # la creación de imágenes docker.

class CreateImage(PipelineJob):
    
    environment: CreateImageEnvironment
    
    def execute(self):
        self.printer.info("Creando imagen docker...")
        build_cmd = DockerTools.build_docker_image(
            name=PredefinedVariables.CI_PROJECT_PATH,
            tag=PredefinedVariables.CI_COMMIT_REF_NAME,
            no_cache=True,
            context=PredefinedVariables.CI_PROJECT_DIR
        )
        if build_cmd.returncode != 0:
            raise exc.ExitError(
                log_message=f"Error creating image: {build_cmd.stdout}\n\n{build_cmd.stderr}",
                user_message="Ha ocurrido un error al crear la imagen docker. "
            )
        self.printer.success("Imagen docker creada correctamente.")
        self.logger.info("Docker image created successfully.")
        self.printer.info("Subiendo imagen docker...")
        login_cmd = DockerTools.login_to_docker_registry(
            registry=PredefinedVariables.CI_REGISTRY,
            username=PredefinedVariables.CI_REGISTRY_USER,
            password=PredefinedVariables.CI_REGISTRY_PASSWORD
        )
        if login_cmd.returncode != 0:
            raise exc.ExitError(
                log_message=f"Error logging in to docker registry: {login_cmd.stdout}\n\n{login_cmd.stderr}",
                user_message="Ha ocurrido un error al iniciar sesión en el registro de Docker. "
            )
        push_cmd = DockerTools.push_docker_image(
            name=PredefinedVariables.CI_PROJECT_PATH,
            tag=PredefinedVariables.CI_COMMIT_REF_NAME,
            registry=PredefinedVariables.CI_REGISTRY
        )
        if push_cmd.returncode != 0:
            raise exc.ExitError(
                log_message=f"Error pushing image: {push_cmd.stdout}\n\n{push_cmd.stderr}",
                user_message="Ha ocurrido un error al subir la imagen docker. "
            )
        self.printer.success("Imagen docker subida correctamente.")
        self.logger.info("Docker image pushed successfully.")
    
    def post_execute(self):
        # No post execution
        pass