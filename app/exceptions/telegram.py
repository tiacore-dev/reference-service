
class TelegramAPIError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"Telegram API Error {status}: {message}")
