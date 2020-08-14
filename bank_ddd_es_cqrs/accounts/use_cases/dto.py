from dataclasses import dataclass


@dataclass(frozen=True)
class AmountDTO:
    dollars: int
    cents: int


@dataclass(frozen=True)
class ClientDetailsDTO:
    social_security_number: int
    first_name: str
    last_name: str
    birthdate: str

