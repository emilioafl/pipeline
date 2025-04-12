from rich.console import Console
from rich.text import Text
from rich.style import Style
from typing import Any

class Printer:
    def __init__(self) -> None:
        self._console = Console(
            force_terminal=True,
            force_interactive=False,
            highlight=False
        )
    
    @property
    def console(self) -> Console:
        return self._console

    def regular(
            self,
            message: str,
            style: str | Style | None = None,
            **kwargs: Any
    ) -> None:
        self._console.print(message, style=style, **kwargs)

    def info(
            self,
            message: str,
            emoji: str = "ℹ️",
            style: str | Style | None = "bold cyan",
            characters: str = "*",
            **kwargs: Any
    ) -> None:
        message = f" {emoji} {message} "
        message = Text(message, style=style)
        self._console.rule(message, style=style, characters=characters, **kwargs)
    
    def warning(
            self,
            message: str,
            emoji: str = "⚠️",
            style: str | Style | None = "bright_yellow",
            **kwargs: Any
    ) -> None:
        self._console.print(f"{emoji} {message}", style=style, **kwargs)
    
    def hint(
            self,
            message: str,
            emoji: str = "💡",
            style: str | Style | None = None,
            **kwargs: Any
    ) -> None:
        self._console.print(f"{emoji} {message}", style=style, **kwargs)
    
    def success(
            self,
            message: str,
            emoji: str = "✅",
            style: str | Style | None = "bright_green",
            **kwargs: Any
    ) -> None:
        self._console.print(f"{emoji} {message}", style=style, **kwargs)
    
    def failure(
            self,
            message: str,
            emoji: str = "❌",
            style: str | Style | None = "bright_red",
            **kwargs: Any
    ) -> None:
        self._console.print(f"{emoji} {message}", style=style, **kwargs)
    
    def critical(
            self,
            message: str,
            emoji: str = "🚨",
            style: str | Style | None = "red",
            **kwargs: Any
    ) -> None:
        self._console.print(f"{emoji} {message}", style=style, **kwargs)
    
    def progress(
            self,
            message: str,
            emoji: str = "⚙️",
            style: str | Style | None = None,
            **kwargs: Any
    ) -> None:
        self._console.print(f"{emoji} {message}", style=style, **kwargs)
    
    def wait(
            self,
            message: str,
            emoji: str = "☕",
            style: str | Style | None = None,
            **kwargs: Any
    ) -> None:
        self._console.print(f"{emoji} {message}", style=style, **kwargs)