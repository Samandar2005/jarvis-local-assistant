from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


APP_COMMANDS = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "explorer": ["explorer.exe"],
}


@dataclass(slots=True)
class ActionResult:
    name: str
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


class WorkspaceSafetyError(ValueError):
    pass


class SystemActions:
    def __init__(self, workspace_dir: Path, command_timeout_seconds: int = 20) -> None:
        self.workspace_dir = workspace_dir.resolve()
        self.command_timeout_seconds = command_timeout_seconds

    def create_file(self, path: str, content: str = "") -> ActionResult:
        target = self._resolve_workspace_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists():
            return ActionResult(
                name="create_file",
                status="warning",
                message=f"{target.name} allaqachon mavjud. Ustiga yozilmadi.",
                details={"path": str(target)},
            )

        final_content = content or self._template_for_path(target)
        target.write_text(final_content, encoding="utf-8")
        return ActionResult(
            name="create_file",
            status="success",
            message=f"{target.name} fayli yaratildi.",
            details={"path": str(target), "bytes": target.stat().st_size},
        )

    def read_file(self, path: str, max_chars: int = 3000) -> ActionResult:
        target = self._resolve_workspace_path(path)
        if not target.exists() or not target.is_file():
            return ActionResult(
                name="read_file",
                status="error",
                message="Fayl topilmadi.",
                details={"path": str(target)},
            )

        content = target.read_text(encoding="utf-8", errors="ignore")
        preview = content[:max_chars]
        if len(content) > max_chars:
            preview += "\n... [qisqartirildi]"

        return ActionResult(
            name="read_file",
            status="success",
            message=f"{target.name} fayli o'qildi.",
            details={"path": str(target), "content": preview},
        )

    def list_files(self, path: str = ".", limit: int = 50) -> ActionResult:
        target = self._resolve_workspace_path(path)
        if not target.exists() or not target.is_dir():
            return ActionResult(
                name="list_files",
                status="error",
                message="Papka topilmadi.",
                details={"path": str(target)},
            )

        entries = []
        for item in sorted(target.iterdir(), key=lambda current: (not current.is_dir(), current.name.lower()))[:limit]:
            item_type = "dir" if item.is_dir() else "file"
            relative_path = item.relative_to(self.workspace_dir).as_posix()
            entries.append({"name": item.name, "type": item_type, "path": relative_path})

        return ActionResult(
            name="list_files",
            status="success",
            message=f"{len(entries)} ta element topildi.",
            details={"path": str(target), "entries": entries},
        )

    def run_python(self, path: str, args: list[str] | None = None) -> ActionResult:
        target = self._resolve_workspace_path(path)
        if not target.exists():
            return ActionResult(
                name="run_python",
                status="error",
                message="Python fayl topilmadi.",
                details={"path": str(target)},
            )

        command = [sys.executable, str(target), *(args or [])]
        completed = subprocess.run(
            command,
            cwd=self.workspace_dir,
            capture_output=True,
            text=True,
            timeout=self.command_timeout_seconds,
        )

        status = "success" if completed.returncode == 0 else "error"
        output = completed.stdout.strip() or completed.stderr.strip() or "Chiqish yo'q."

        return ActionResult(
            name="run_python",
            status=status,
            message=f"Skript bajarildi. Exit code: {completed.returncode}",
            details={
                "path": str(target),
                "returncode": completed.returncode,
                "output": output[:4000],
                "command": command,
            },
        )

    def open_browser(self, url: str) -> ActionResult:
        webbrowser.open(url)
        return ActionResult(
            name="open_browser",
            status="success",
            message=f"Brauzerga yuborildi: {url}",
            details={"url": url},
        )

    def open_path(self, path: str = ".") -> ActionResult:
        target = self._resolve_workspace_path(path)
        if not target.exists():
            return ActionResult(
                name="open_path",
                status="error",
                message="Manzil topilmadi.",
                details={"path": str(target)},
            )

        if hasattr(os, "startfile"):
            os.startfile(str(target))
        else:
            webbrowser.open(target.as_uri())

        return ActionResult(
            name="open_path",
            status="success",
            message=f"Manzil ochildi: {target}",
            details={"path": str(target)},
        )

    def launch_app(self, app_name: str) -> ActionResult:
        command = APP_COMMANDS.get(app_name)
        if not command:
            return ActionResult(
                name="launch_app",
                status="error",
                message=f"{app_name} ruxsat etilgan ilovalar ro'yxatida yo'q.",
                details={"allowed_apps": sorted(APP_COMMANDS)},
            )

        subprocess.Popen(command)
        return ActionResult(
            name="launch_app",
            status="success",
            message=f"{app_name} ishga tushirildi.",
            details={"command": command},
        )

    def _resolve_workspace_path(self, user_path: str) -> Path:
        candidate = (self.workspace_dir / user_path).resolve()

        try:
            candidate.relative_to(self.workspace_dir)
        except ValueError as exc:
            raise WorkspaceSafetyError("Faqat workspace ichidagi yo'llarga ruxsat bor.") from exc

        return candidate

    def _template_for_path(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".py":
            return (
                "def main() -> None:\n"
                "    print(\"Assistant yaratgan Python skript ishladi\")\n\n\n"
                "if __name__ == \"__main__\":\n"
                "    main()\n"
            )
        if suffix == ".html":
            return (
                "<!DOCTYPE html>\n"
                "<html lang=\"uz\">\n"
                "<head>\n"
                "  <meta charset=\"UTF-8\" />\n"
                "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
                "  <title>New Page</title>\n"
                "</head>\n"
                "<body>\n"
                "  <h1>Yangi sahifa</h1>\n"
                "</body>\n"
                "</html>\n"
            )
        if suffix == ".js":
            return "console.log('Assistant yaratgan JS fayl');\n"
        if suffix == ".css":
            return "body {\n    font-family: Bahnschrift, 'Segoe UI Variable', sans-serif;\n}\n"
        return ""
