from agentbay.api.base_service import BaseService
from agentbay.exceptions import AgentBayError, CommandError
from agentbay.model import ApiResponse


class CommandResult(ApiResponse):
    """Result of command execution operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        output: str = "",
        error_message: str = "",
    ):
        """
        Initialize a CommandResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            output (str, optional): The command output.
            error_message (str, optional): Error message if the operation failed.
        """
        super().__init__(request_id)
        self.success = success
        self.output = output
        self.error_message = error_message


class CodeExecutionResult(ApiResponse):
    """Result of code execution operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        result: str = "",
        error_message: str = "",
    ):
        """
        Initialize a CodeExecutionResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            result (str, optional): The execution result.
            error_message (str, optional): Error message if the operation failed.
        """
        super().__init__(request_id)
        self.success = success
        self.result = result
        self.error_message = error_message


class Command(BaseService):
    """
    Handles command execution operations in the AgentBay cloud environment.
    """

    def _handle_error(self, e):
        """
        Convert AgentBayError to CommandError for compatibility.

        Args:
            e (Exception): The exception to convert.

        Returns:
            CommandError: The converted exception.
        """
        if isinstance(e, CommandError):
            return e
        if isinstance(e, AgentBayError):
            return CommandError(str(e))
        return e

    def execute_command(self, command: str, timeout_ms: int = 1000) -> CommandResult:
        """
        Execute a command in the cloud environment with a specified timeout.

        Args:
            command: The command to execute.
            timeout_ms: The timeout for the command execution in milliseconds.

        Returns:
            CommandResult: Result object containing success status, command output,
                and error message if any.
        """
        try:
            args = {"command": command, "timeout_ms": timeout_ms}

            result = self._call_mcp_tool("shell", args)
            print(f"Command executed response: {result}")

            if result.success:
                return CommandResult(
                    request_id=result.request_id,
                    success=True,
                    output=result.data,
                )
            else:
                return CommandResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to execute command",
                )
        except CommandError as e:
            return CommandResult(request_id="", success=False, error_message=str(e))
        except Exception as e:
            return CommandResult(
                request_id="",
                success=False,
                error_message=f"Failed to execute command: {e}",
            )

    def run_code(
        self, code: str, language: str, timeout_s: int = 300
    ) -> CodeExecutionResult:
        """
        Execute code in the specified language with a timeout.

        Args:
            code: The code to execute.
            language: The programming language of the code. Must be either 'python'
                or 'javascript'.
            timeout_s: The timeout for the code execution in seconds. Default is 300s.

        Returns:
            CodeExecutionResult: Result object containing success status, execution
                result, and error message if any.

        Raises:
            CommandError: If the code execution fails or if an unsupported language is
                specified.
        """
        try:
            # Validate language
            if language not in ["python", "javascript"]:
                return CodeExecutionResult(
                    request_id="",
                    success=False,
                    error_message=f"Unsupported language: {language}. Supported "
                    "languages are 'python' and 'javascript'",
                )

            args = {"code": code, "language": language, "timeout_s": timeout_s}
            result = self._call_mcp_tool("run_code", args)
            print(f"Run code response: {result}")

            if result.success:
                return CodeExecutionResult(
                    request_id=result.request_id,
                    success=True,
                    result=result.data,
                )
            else:
                return CodeExecutionResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to run code",
                )
        except CommandError as e:
            return CodeExecutionResult(
                request_id="", success=False, error_message=str(e)
            )
        except Exception as e:
            return CodeExecutionResult(
                request_id="",
                success=False,
                error_message=f"Failed to run code: {e}",
            )
