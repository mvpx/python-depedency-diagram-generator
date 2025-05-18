from enum import StrEnum


class GeneratorType(StrEnum):
    Text = "text"
    Mermaid = "mermaid"
    ASCII = "ascii"

    @classmethod
    def get_options(cls) -> list:
        """Returns a list of all the strings defined in the enumeration."""
        return [item.value for item in cls]