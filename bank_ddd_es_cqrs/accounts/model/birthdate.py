from datetime import datetime
from dataclasses import dataclass, field, InitVar


@dataclass(frozen=True)
class Birthdate:
    value: str
    date: datetime = field(init=False)

    def __post_init__(self) -> None:
        try:
            self.__dict__['date'] = datetime.strptime(self.value, '%d/%m/%Y')
        except ValueError:
            raise ValueError(f'Could not parse date - {self.value}')

    @property
    def year(self) -> int:
        return self.date.year

    @property
    def day(self) -> int:
        return self.date.day

    @property
    def month(self) -> int:
        return self.date.month
