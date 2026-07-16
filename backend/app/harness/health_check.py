from dataclasses import dataclass


@dataclass
class HealthStatus:
    tool_name: str
    healthy: bool
    detail: str = ""


class HealthChecker:
    """Pings external tools/services before agents are allowed to use them."""

    @staticmethod
    def check_ocr_engine() -> HealthStatus:
        # Placeholder — real check added when OCR service is built (later step)
        return HealthStatus(tool_name="ocr_engine", healthy=True, detail="stub OK")

    @staticmethod
    def check_llm_service() -> HealthStatus:
        # Placeholder — real check added when LLM service is built (later step)
        return HealthStatus(tool_name="llm_service", healthy=True, detail="stub OK")

    @classmethod
    def check_all(cls) -> list[HealthStatus]:
        return [cls.check_ocr_engine(), cls.check_llm_service()]