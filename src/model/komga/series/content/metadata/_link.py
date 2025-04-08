class Link:
    def __init__(self):
        self.label: str
        self.url: str

    @classmethod
    def new(cls, label: str, url: str) -> "Link":
        instance = cls()
        instance.label = label
        instance.url = url
        return instance

    @classmethod
    def from_json(cls, resp: dict) -> "Link":
        return Link.new(resp["label"], resp["url"])
