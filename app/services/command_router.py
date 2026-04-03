from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


APP_ALIASES = {
    "notepad": "notepad",
    "bloknot": "notepad",
    "calculator": "calculator",
    "calc": "calculator",
    "kalkulyator": "calculator",
    "explorer": "explorer",
    "fayl menejer": "explorer",
}

SITE_ALIASES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
}


@dataclass(slots=True)
class CommandPlan:
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    summary: str = ""


class CommandRouter:
    def route(self, message: str) -> CommandPlan | None:
        text = self._normalize(message)

        for matcher in (
            self._match_help,
            self._match_open_browser,
            self._match_launch_app,
            self._match_create_file,
            self._match_run_python,
            self._match_read_file,
            self._match_list_files,
            self._match_open_path,
        ):
            plan = matcher(message, text)
            if plan:
                return plan

        return None

    def _normalize(self, message: str) -> str:
        return re.sub(r"\s+", " ", message.strip().lower())

    def _normalize_target(self, target: str) -> str:
        cleaned = target.strip("'\" ").lower()
        if cleaned in {"workspace", "project", "loyiha", "root"}:
            return "."
        return target.strip("'\" ")

    def _match_help(self, _: str, text: str) -> CommandPlan | None:
        if any(
            key in text
            for key in (
                "nima qila olasan",
                "help",
                "yordam",
                "capabilities",
                "what can you do",
            )
        ):
            return CommandPlan(action="help", summary="Yordam va imkoniyatlarni ko'rsatish")
        return None

    def _match_open_browser(self, original: str, text: str) -> CommandPlan | None:
        if not any(
            phrase in text
            for phrase in ("open browser", "brauzer", "browser", "saytni och", "website", "open google", "open youtube")
        ):
            return None

        url_match = re.search(r"(https?://\S+|www\.\S+)", original, re.IGNORECASE)
        if url_match:
            url = url_match.group(1)
            if url.startswith("www."):
                url = f"https://{url}"
        else:
            url = next(
                (link for alias, link in SITE_ALIASES.items() if alias in text),
                "https://www.google.com",
            )

        return CommandPlan(
            action="open_browser",
            params={"url": url},
            summary=f"Brauzerda {url} manzilini ochish",
        )

    def _match_launch_app(self, _: str, text: str) -> CommandPlan | None:
        if not any(token in text for token in ("open", "launch", "och", "ishga tushir")):
            return None

        for alias, app_name in APP_ALIASES.items():
            if alias in text:
                return CommandPlan(
                    action="launch_app",
                    params={"app_name": app_name},
                    summary=f"{app_name} ilovasini ishga tushirish",
                )
        return None

    def _match_create_file(self, original: str, text: str) -> CommandPlan | None:
        if not any(token in text for token in ("create file", "make file", "fayl yarat", "file yarat", "yangi fayl")):
            return None

        path_match = re.search(
            r"(?:create|make|yarat|yangi)\s+(?:a\s+)?(?:new\s+)?file(?:\s+named)?\s+(?P<path>\"[^\"]+\"|'[^']+'|\S+)",
            original,
            re.IGNORECASE,
        )
        if not path_match:
            path_match = re.search(
                r"(?:fayl(?:ni)?\s+yarat|yangi\s+fayl)\s+(?P<path>\"[^\"]+\"|'[^']+'|\S+)",
                original,
                re.IGNORECASE,
            )
        if not path_match:
            return None

        raw_path = path_match.group("path").strip("'\"")
        content_match = re.search(
            r"(?:with content|content|ichiga|matn)\s*[:\-]?\s*(?P<content>.+)$",
            original,
            re.IGNORECASE,
        )

        return CommandPlan(
            action="create_file",
            params={
                "path": raw_path,
                "content": content_match.group("content").strip() if content_match else "",
            },
            summary=f"{raw_path} faylini yaratish",
        )

    def _match_run_python(self, original: str, text: str) -> CommandPlan | None:
        if not any(
            token in text
            for token in (
                "run python",
                "run script",
                "python script",
                "skriptni ishga tushir",
                "python fayl",
            )
        ):
            return None

        path_match = re.search(
            r"(?P<path>\"[^\"]+\.py\"|'[^']+\.py'|[^\s]+\.py)",
            original,
            re.IGNORECASE,
        )
        if not path_match:
            return None

        raw_path = path_match.group("path").strip("'\"")
        args_match = re.search(r"--\s*(?P<args>.+)$", original)
        args = args_match.group("args").split() if args_match else []

        return CommandPlan(
            action="run_python",
            params={"path": raw_path, "args": args},
            summary=f"{raw_path} Python skriptini ishga tushirish",
        )

    def _match_read_file(self, original: str, text: str) -> CommandPlan | None:
        if not any(token in text for token in ("read file", "show file", "faylni o'qib", "faylni korsat", "faylni ko'rsat")):
            return None

        path_match = re.search(
            r"(?:read|show)\s+file\s+(?P<path>\"[^\"]+\"|'[^']+'|\S+)",
            original,
            re.IGNORECASE,
        )
        if not path_match:
            path_match = re.search(
                r"fayl(?:ni)?\s+(?:o'qib\s+ber|ko'rsat|korsat)\s+(?P<path>\"[^\"]+\"|'[^']+'|\S+)",
                original,
                re.IGNORECASE,
            )
        if not path_match:
            return None

        raw_path = path_match.group("path").strip("'\"")
        return CommandPlan(
            action="read_file",
            params={"path": raw_path},
            summary=f"{raw_path} faylini o'qish",
        )

    def _match_list_files(self, original: str, text: str) -> CommandPlan | None:
        if not any(
            token in text
            for token in (
                "list files",
                "show files",
                "fayllarni ko'rsat",
                "papkadagi fayllar",
                "files in",
            )
        ):
            return None

        path_match = re.search(
            r"(?:in|inside|papka)\s+(?P<path>\"[^\"]+\"|'[^']+'|\S+)",
            original,
            re.IGNORECASE,
        )
        if not path_match:
            path_match = re.search(
                r"(?P<path>\"[^\"]+\"|'[^']+'|\S+)\s+ichidagi",
                original,
                re.IGNORECASE,
            )
        target = self._normalize_target(path_match.group("path")) if path_match else "."

        summary_target = "workspace" if target == "." else target

        return CommandPlan(
            action="list_files",
            params={"path": target},
            summary=f"{summary_target} ichidagi fayllarni ko'rsatish",
        )

    def _match_open_path(self, original: str, text: str) -> CommandPlan | None:
        if not any(token in text for token in ("open folder", "open path", "papkani och", "papka och", "folderni och")):
            return None

        path_match = re.search(
            r"(?:folder|path|papka)\s+(?P<path>\"[^\"]+\"|'[^']+'|\S+)",
            original,
            re.IGNORECASE,
        )
        target = self._normalize_target(path_match.group("path")) if path_match else "."

        summary_target = "workspace" if target == "." else target

        return CommandPlan(
            action="open_path",
            params={"path": target},
            summary=f"{summary_target} manzilini ochish",
        )

    def capabilities_text(self) -> str:
        return (
            "Men quyidagi amallarni qila olaman: brauzer ochish, notepad yoki kalkulyatorni ishga tushirish, "
            "workspace ichida fayl yaratish, fayllarni ko'rsatish, faylni o'qish va Python skriptini ishga tushirish. "
            "Agar OPENAI kaliti ulansa, erkin AI chat va kod bo'yicha javoblar ham beradi."
        )
