from os import getenv

class PipelineJobEnvironment:
    def __init__(self):
        self.SSL_VERIFY: bool = getenv("SSL_VERIFY", "True").lower() == "true"
        self.FRAMEWORK: str = getenv("FRAMEWORK", "")
        self.TEMPLATES_DIR: str = getenv("TEMPLATES_DIR", "")