class AlternativeTitle:
    def __init__(self):
        self.label: str
        self.title: str

    @classmethod
    def new(cls, label: str, title: str) -> "AlternativeTitle":
        instance = AlternativeTitle()
        instance.label = label
        instance.title = title
        return instance

    @classmethod
    def from_json(cls, resp: dict) -> "AlternativeTitle":
        return AlternativeTitle.new(resp["label"], resp["title"])
