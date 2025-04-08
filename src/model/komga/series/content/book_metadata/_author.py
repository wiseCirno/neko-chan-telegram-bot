class Author:
    def __init__(self):
        self.name: str = ""
        self.role: str = ""

    @classmethod
    def new(cls, name: str, role: str) -> "Author":
        instance = Author()
        instance.name = name
        instance.role = role
        return instance

    @classmethod
    def from_json(cls, resp: dict) -> "Author":
        return Author.new(resp["name"], resp["role"])
