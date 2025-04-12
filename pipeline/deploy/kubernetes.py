import pipeline.exceptions as exc

from os import getenv
from time import sleep
from kubernetes import client, config, utils

from pipeline.deploy.base import DeployManager, BaseDeployEnvironment
from pipeline.common.gitlab import PredefinedVariables

class KubernetesDeployEnvironment(BaseDeployEnvironment):
    def __init__(self):
        super().__init__()
        self.KUBE_CLUSTER_CONFIG_FILE_PATH = getenv("KUBE_CLUSTER_CONFIG")
        self.NAMESPACE = getenv("KUBE_NAMESPACE")
        self.KUBE_MANIFEST = f"{PredefinedVariables.CI_PROJECT_DIR}/kubernetes.yml"
        self.IMAGE_NAME = f"{PredefinedVariables.CI_REGISTRY}/{PredefinedVariables.CI_PROJECT_PATH}:{PredefinedVariables.CI_COMMIT_REF_NAME}"

class KubernetesManager(DeployManager):
    
    environment: KubernetesDeployEnvironment
    
    def _load_config(self):
        super()._load_config()
        self.environment = KubernetesDeployEnvironment()
        super()._check_environment()
    
    def authenticate(self):
        configuration = client.Configuration()
        config.load_kube_config(
            config_file=self.environment.KUBE_CLUSTER_CONFIG_FILE_PATH,
            client_configuration=configuration
        )
        configuration.verify_ssl = self.environment.SSL_VERIFY
        self.k8s_client = client.ApiClient(configuration=configuration)
    
    def execute(self):
        self.authenticate()
        self.printer.info("Reemplazando variables en el manifiesto...")
        self.replace_template_variables()
        self.printer.success("Variables reemplazadas correctamente.")
        self.printer.info("Desplegando el servicio con Kubernetes...")
        try:
            utils.create_from_yaml(
                k8s_client=self.k8s_client,
                yaml_file=self.environment.KUBE_MANIFEST,
                verbose=True
            )
        except Exception as e:
            raise exc.ExitError(
                user_message=f"Error al desplegar el servicio con Kubernetes.",
                log_message=f"An error occurred while deploying the service with Kubernetes: {e}",
            )
        self.printer.info("Esperando a que el servicio esté disponible...")
        healthy = self.check_health(
            deployment_name=PredefinedVariables.CI_PROJECT_NAME
        )
        if not healthy:
            raise exc.ExitError(
                user_message="El servicio no se pudo desplegar correctamente.",
                log_message="The service is not healthy after deployment."
            )
        self.printer.success("El servicio se ha desplegado correctamente.")
        self.logger.info("Service deployed successfully.")
    
    def replace_template_variables(self):
        with open(self.environment.KUBE_MANIFEST, "r+") as file:
            manifest = file.read()
            manifest = manifest.replace(
                "$IMAGE_NAME",
                self.environment.IMAGE_NAME
            )
            file.seek(0)
            file.truncate()
            file.write(manifest)
      
    def check_health(
            self,
            deployment_name: str,
            n_healthchecks: int = 7,
            interval: int = 10
        ) -> bool:
        service_up = False
        for _ in range(n_healthchecks):
            sleep(interval)
            deployment = self.get_deployment(deployment_name)
            replicas = deployment.status.replicas
            ready_replicas = deployment.status.ready_replicas \
                if deployment.status.ready_replicas else 0
            
            if replicas == ready_replicas:
                self.printer.success(f"Estado del servicio: UP {ready_replicas}/{replicas}")
                service_up = True
            else:
                self.printer.failure(f"Estado del servicio: DOWN {ready_replicas}/{replicas}")
                service_up = False
        return service_up
    
    def get_deployment(self, name: str):
        api_v1 = client.AppsV1Api(api_client=self.k8s_client)
        deployment = api_v1.read_namespaced_deployment(
            name=name,
            namespace=self.environment.NAMESPACE
        )
        return deployment

