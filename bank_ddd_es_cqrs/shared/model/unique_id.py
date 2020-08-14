import uuid
from dataclasses import dataclass, field


def uuid4_as_string() -> str:
    return str(uuid.uuid4())


@dataclass(frozen=True)
class UniqueID:
    value: str = field(default_factory=uuid4_as_string)

    def __str__(self) -> str:
        return self.value
