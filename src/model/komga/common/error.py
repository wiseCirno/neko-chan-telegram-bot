import json
from datetime import datetime


class KomgaViolationError(BaseException):
    def __init__(self, resp: json):
        self.field_name = resp["fieldName"]
        self.message = resp["message"]
        super().__init__(self.message)

    def __str__(self):
        return f"<{self.field_name}> {self.message}"


class KomgaMultipleViolationErrors(Exception):
    def __init__(self, violations: list[KomgaViolationError]):
        self.violations = violations
        formatted_messages = []
        for index, violation in enumerate(self.violations):
            formatted_messages.append(f"{index + 1}. {str(violation)}")
        super().__init__(f"Multiple Komga violation errors occurred:\n{chr(10).join(formatted_messages)}")

    def __str__(self):
        formatted_messages = []
        for index, violation in enumerate(self.violations):
            formatted_messages.append(f"{index + 1}. {str(violation)}")
        return f"Multiple Komga violation errors occurred:\n{chr(10).join(formatted_messages)}"


class KomgaError(BaseException):
    def __init__(self, resp: dict):
        self.timestamp = datetime.fromisoformat(resp["timestamp"])
        self.status = resp["status"]
        self.error = resp["error"]
        self.message = resp["message"]
        self.path = resp["path"]
        super().__init__(self.message)

    def __str__(self):
        return f"Komga API Error: {self.status} - {self.error}\n" \
               f"Message: {self.message}\n" \
               f"Path: {self.path}\n" \
               f"Timestamp: {self.timestamp}"
