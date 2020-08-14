from dataclasses import dataclass


@dataclass(frozen=True)
class SocialSecurityNumber:
    value: int

    def __post_init__(self) -> None:
        if len(str(self.value)) != 9:
            raise ValueError(f'Client social security number value is not 9 integers - {self.value}')
