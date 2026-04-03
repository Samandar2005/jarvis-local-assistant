from __future__ import annotations

from dataclasses import asdict

from app.config import Settings
from app.schemas import ActionPayload, ChatResponse
from app.services.command_router import CommandPlan, CommandRouter
from app.services.llm_service import LLMService
from app.services.system_actions import ActionResult, SystemActions, WorkspaceSafetyError


SYSTEM_PROMPT = """
Sen Windows kompyuteriga ulangan lokal AI yordamchisan.
Doim foydalanuvchiga o'zbek tilida javob ber.
Vazifang:
- Python, HTML, CSS, JavaScript va avtomatlashtirish bo'yicha yordam berish
- foydalanuvchi maqsadini tez tushunish
- qisqa, amaliy va bajariladigan javob yozish
- kerak bo'lsa reja, kod va yaxshilash tavsiyalarini berish

Kompyuter amallari alohida tool qatlami orqali bajariladi. Agar foydalanuvchi umumiy savol bersa,
faqat foydali va amaliy javob qaytar.
""".strip()


class AssistantService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.router = CommandRouter()
        self.actions = SystemActions(
            workspace_dir=settings.workspace_dir,
            command_timeout_seconds=settings.command_timeout_seconds,
        )
        self.llm = LLMService(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    def handle_message(self, message: str) -> ChatResponse:
        plan = self.router.route(message)
        if plan:
            return self._execute_plan(plan)

        try:
            llm_reply = self.llm.ask(message=message, system_prompt=SYSTEM_PROMPT)
            if llm_reply:
                return ChatResponse(reply=llm_reply, source="llm")
        except Exception as exc:
            return ChatResponse(
                reply=(
                    "LLM bilan bog'lanishda xato yuz berdi. Kalit va model nomini tekshiring.\n\n"
                    f"Xato: {exc}"
                ),
                source="fallback",
            )

        fallback_reply = (
            "To'liq AI suhbat hozircha yoqilmagan. `.env` ichiga `OPENAI_API_KEY` va `OPENAI_MODEL` qo'shsangiz, "
            "men erkin chat, kod tahlili va tavsiyalarni ham bera olaman.\n\n"
            f"Hozirgi lokal imkoniyatlar: {self.router.capabilities_text()}"
        )
        return ChatResponse(reply=fallback_reply, source="fallback")

    def _execute_plan(self, plan: CommandPlan) -> ChatResponse:
        if plan.action == "help":
            return ChatResponse(
                reply=self.router.capabilities_text(),
                source="tool",
            )

        try:
            method = getattr(self.actions, plan.action)
            result: ActionResult = method(**plan.params)
        except WorkspaceSafetyError as exc:
            result = ActionResult(
                name=plan.action,
                status="error",
                message=str(exc),
            )
        except Exception as exc:  # pragma: no cover
            result = ActionResult(
                name=plan.action,
                status="error",
                message=f"Amalni bajarishda xato yuz berdi: {exc}",
            )

        reply = self._format_tool_reply(plan, result)
        return ChatResponse(
            reply=reply,
            source="tool",
            action=ActionPayload(**asdict(result)),
        )

    def _format_tool_reply(self, plan: CommandPlan, result: ActionResult) -> str:
        header = f"Amal: {plan.summary}\nHolat: {result.status}\nNatija: {result.message}"

        if result.name == "list_files" and result.details.get("entries"):
            lines = [
                f"- [{entry['type']}] {entry['path']}"
                for entry in result.details["entries"]
            ]
            return f"{header}\n\nTopilganlar:\n" + "\n".join(lines)

        if result.name == "read_file" and result.details.get("content"):
            return f"{header}\n\nFayl preview:\n{result.details['content']}"

        if result.name == "run_python" and result.details.get("output"):
            return f"{header}\n\nChiqish:\n{result.details['output']}"

        return header
