class Echo:
    name = "Echo"
    description = "say again {the input}."

    def __init__(self) -> None:
        pass

    def __call__(self, command: str) -> str:
        return command
