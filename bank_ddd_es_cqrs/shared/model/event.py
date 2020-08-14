import attr

# Note:
# When dealing with the events we use the `attr` package for the following reasons:
#  - ATM `dataclasses` does not support a keyword only feature, we need it because of the following reason
#  - when using dataclass on a parent class that has default argument (such as version), it will throw error
#    that there is non default parameters after default parameter.


@attr.s(kw_only=True, frozen=True)
class BaseEvent:
    operation_id: str = attr.ib()
    version: int = attr.ib(default=1)
