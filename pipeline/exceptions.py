from typing import Callable, Optional
from dataclasses import dataclass
from uuid import uuid4
from os.path import dirname

import pipeline
from pipeline import logger
from pipeline.common.printer import Printer

class BaseError(Exception):
    log_message: str = "The job execution did not complete successfully."
    user_message: Optional[str] = "Ha ocurrido un error."
    user_hint: Optional[str] = "Por favor revisar los logs para más detalles."

    def __init__(
        self,
        log_message: str = log_message,
        user_message: Optional[str] = user_message,
        user_hint: Optional[str] = user_hint,
        *args
    ) -> None:
        super().__init__(*args)
        self.log_message = log_message
        self.user_message = user_message
        self.user_hint = user_hint

class ExitError(BaseError):
    """
    Base class for all exit errors.
    """
    def __init__(
        self,
        code: str = 1,
        force_exit: bool = False,
        log_message: str = BaseError.log_message,
        critical: bool = False,
        user_message: Optional[str] = BaseError.user_message,
        user_hint: Optional[str] = BaseError.user_hint,
        *args
    ):
        super().__init__(log_message, user_message, user_hint, *args)
        self.code = code
        self.force_exit = force_exit
        self.log_message = log_message
        self.critical = critical
        

# Job Errors
class JobNotFoundError(BaseError): ...

@dataclass
class TracebackInfo:
    filename: str
    line_no: int
    func_name: str
    func_args: dict

def get_deepest_app_frame(exception: Exception) -> TracebackInfo:
    # Get the application root directory
    app_root = dirname(pipeline.__file__)
    
    tb = exception.__traceback__
    app_frame = None
    next_app_frame = None

    # Traverse the traceback
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        # Check if the file is under the application directory
        if not filename.startswith(app_root):
            break
        app_frame = tb
        tb = tb.tb_next
    
    if app_frame:
        filename = app_frame.tb_frame.f_code.co_filename
        line_no = app_frame.tb_lineno
        func_call_frame = tb if tb != None else app_frame
        func_name = func_call_frame.tb_frame.f_code.co_name
        # Get function arguments
        func_args = func_call_frame.tb_frame.f_locals
        return TracebackInfo(
            filename=filename,
            line_no=line_no,
            func_name=func_name,
            func_args=func_args
        )
    return TracebackInfo()

def handle_errors(e: Exception):
    printer = Printer()
    error_id = f"ERR-{uuid4()}"
    traceback_info = get_deepest_app_frame(e)
    
    function_call_args = [f"{key}={value}" for key, value in traceback_info.func_args.items()]
    logger.critical(f"{repr(e)} in {traceback_info.filename}, line {traceback_info.line_no}", extra={"error_id": error_id, "call": f"{traceback_info.func_name}({','.join(function_call_args)})"})
    if not issubclass(type(e), BaseError):
        user_message = BaseError.user_message
        user_hint = BaseError.user_hint
    else:
        user_message = e.user_message
        user_hint = e.user_hint
        logger.error(f"Log message: {e.log_message}")

    printer.critical(f"{user_message} - {error_id}")
    printer.hint(user_hint)

def handle_exit_errors(e: ExitError):
    if e.critical:
        handle_errors(e)
        return
    printer = Printer()
    if e.user_message:
        printer.critical(e.user_message)
    if e.user_hint:
        printer.hint(e.user_hint)
    logger.info(f"Script exited with message: {e.log_message}")

# Error Catcher
def catch_errors(func: Callable):
    """
    Generic exception catcher.
    """
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ExitError as e:
            handle_exit_errors(e)
            exit(e.code)
        except Exception as e:
            handle_errors(e)
            exit(1)
    return wrapper