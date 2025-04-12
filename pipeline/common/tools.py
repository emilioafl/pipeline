from subprocess import run, CompletedProcess, PIPE, CalledProcessError
from typing import Any
from shlex import split

import pipeline.exceptions as exc

class CommandTools:
    @staticmethod
    def run_command(
        command: str,
        workdir: str = ".",
        input: str = "",
        stdout: int | None = PIPE,
        stderr: int | None = PIPE,
        shell: bool = False,
        split_cmd: bool = True,
        **kwargs: Any
    ) -> CompletedProcess:
        """
        Runs a command.

        :param str command: The string of the command you want to run.
        :param str workdir: The directory where the command will be executed.
        :param str input: Passes the given input as stdin.
        :param int stdout: The stdout mode. Defaults to PIPE.
        :param int stderr: The stderr mode. Defaults to PIPE.
        :param bool shell: Whether to run the command in a shell or not.
        """
        if split_cmd:
            command = split(command)
        try:
            exec_command = run(command,
                            shell=shell,
                            stdout=stdout,
                            stderr=stderr,
                            input=input,
                            text=True,
                            check=True,
                            cwd=workdir,
                            **kwargs)
        except CalledProcessError as e:
            return e
        return exec_command

class DockerTools:
    @staticmethod
    def login_to_docker_registry(
        registry: str,
        username: str,
        password: str
    ) -> CompletedProcess:
        """
        Logs in to a Docker registry.

        :param str registry: The Docker registry URL.
        :param str username: The username to log in.
        :param str password: The password to log in.
        """
        command = f"docker login {registry} -u {username} --password-stdin"
        return CommandTools.run_command(
            command=command,
            input=password
        )
    
    @staticmethod
    def build_docker_image(
            name: str,
            tag: str,
            context: str = ".",
            no_cache: bool = False,
            dockerfile_path: str = "",
            input_args: dict = {}
        ) -> CompletedProcess | None:
        """
        Builds the docker image with the given parameters.

        :param str name: The name of the image.
        :param str tag: The tag of the image.
        :param str context: The build context. Defaults to the current directory.
        :param bool no_cache: Whether to build without cache. Defaults to False.
        :param str dockerfile_path: The path to the Dockerfile. Defaults to the current directory.
        :param dict input_args: A dictionary of build arguments.

        :returns: The output of the build command.
        :rtypes: CompletedProcess | None
        """

        build_command = f"docker build -t {name}:{tag} "

        if dockerfile_path != "":
            build_command += f"-f {dockerfile_path} "
        
        if no_cache:
            build_command += "--no-cache "
        
        for arg_name, arg_value in input_args.items():
            build_command += f"--build-arg {arg_name}={arg_value} "
        
        build_command += context

        cmd_out = CommandTools.run_command(command=build_command)
        return cmd_out

    @staticmethod
    def push_docker_image(
            name: str,
            tag: str,
            registry: str
        ) -> CompletedProcess:
        """
        Pushes the docker image to the given registry.

        :param str name: The name of the image.
        :param str tag: The tag of the image.
        :param str registry: The Docker registry URL.

        :returns: The output of the push command.
        :rtypes: CompletedProcess
        """
        push_command = f"docker push {registry}/{name}:{tag}"
        return CommandTools.run_command(command=push_command)