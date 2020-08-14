from dataclasses import dataclass


@dataclass(frozen=True)
class StringValueObject:
    value: str

    def __post_init__(self) -> None:
        """
        Validate that the string is not empty
        """
        if not len(self.value):
            raise ValueError(f'Invalid value for {self.__class__.__name__} - {self.value}')


class FirstName(StringValueObject):
    pass


class LastName(StringValueObject):
    pass
