class VersionError(Exception):
    """Base version error"""


class VersionParseError(VersionError, ValueError):
    """Unable to parse version"""

    schema: str
    value: str

    def __init__(self, schema: str, value: str) -> None:
        super().__init__(
            "Unable to parse version using given schema & value. Expected "
            f"schema: {schema}, value: {value}"
        )

        self.schema = schema
        self.value = value
