

class AppException(Exception):
    status_code: int = 400
    code: str = "APPLICATION_ERROR"
    detail: str = "Application error"

    def __init__(self, detail: str | None = None) -> None:
        if detail:
            self.detail = detail