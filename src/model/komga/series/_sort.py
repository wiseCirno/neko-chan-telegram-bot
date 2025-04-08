class Sort:
    def __init__(self):
        self.empty: bool
        self.sorted: bool
        self.unsorted: bool

    @classmethod
    def new(cls, empty: bool, sorted: bool, unsorted: bool):
        instance = cls()
        instance.empty = empty
        instance.sorted = sorted
        instance.unsorted = unsorted
        return instance

    @classmethod
    def from_json(cls, resp: dict) -> "Sort":
        return Sort.new(resp["empty"], resp["sorted"], resp["unsorted"])
