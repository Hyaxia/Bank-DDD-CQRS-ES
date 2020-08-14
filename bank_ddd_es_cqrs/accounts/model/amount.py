import math
from typing import Tuple
from dataclasses import dataclass


@dataclass(frozen=True)
class Amount:
    dollars: int
    cents: int = 0

    def __post_init__(self) -> None:
        dollars, cents = self._convert_cents_to_dollars_if_possible()
        self.__dict__['dollars'] = dollars + self.dollars
        self.__dict__['cents'] = cents

    def _convert_cents_to_dollars_if_possible(self) -> Tuple[int, int]:
        cents_in_dollars = self.cents // 100
        dollars = 0 if cents_in_dollars < 0 else cents_in_dollars
        return dollars, self.cents - dollars * 100

    def __add__(self, other: 'Amount') -> 'Amount':
        return Amount(self.dollars + other.dollars, self.cents + other.cents)

    def __gt__(self, other: 'Amount') -> bool:
        if self.dollars != other.dollars:
            return self.dollars > other.dollars
        return self.cents > other.cents

    def __ge__(self, other: 'Amount') -> bool:
        if self.dollars > other.dollars:
            return True
        elif self.dollars == other.dollars:
            if self.cents >= other.cents:
                return True
        return False

    def __sub__(self, other: 'Amount') -> 'Amount':
        return Amount(self.dollars - other.dollars, self.cents - other.cents)

    def __neg__(self) -> 'Amount':
        return Amount(-self.dollars, -self.cents)

    @property
    def total_dollars(self) -> float:
        return self.dollars + self.cents / 100

    @property
    def total_cents(self) -> int:
        return self.dollars * 100 + self.cents

    def _get_2_after_decimal(self, num: float) -> int:
        return int(str(round(num, 2)).split('.')[-1])

    def _cents_and_dollars_from_float(self, dollars: float) -> Tuple[int, int]:
        float_cent_divided_by_10, float_dollars = math.modf(dollars)
        return int(float_cent_divided_by_10 * 100), int(float_dollars)

    def __truediv__(self, other: 'Amount') -> 'Amount':
        if other > self:
            return self

        if self.dollars == 0:
            return Amount(0, int(self.cents / other.cents))

        if other.dollars == 0:
            result = (self.total_cents / other.total_cents) / 100
            cents, dollars = self._cents_and_dollars_from_float(result)
            return Amount(dollars, cents)

        result = self.total_dollars / other.total_dollars
        cents_unprocessed, dollars = math.modf(result)  # type: ignore
        return Amount(int(dollars), self._get_2_after_decimal(cents_unprocessed))
