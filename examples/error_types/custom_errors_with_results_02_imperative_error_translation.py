from __future__ import annotations

import abc
import typing as t
from dataclasses import dataclass
from enum import IntEnum

from typing_extensions import Never, Self, reveal_type

from fp import Err, Result
from fp_extras.error import Error

T = t.TypeVar("T")


def assert_never(x: Never) -> Never:  # type: ignore
    pass


# Using IntEnum for code


class CodeInContext1(IntEnum):
    FAIL_TO_DO_SOMETHING = 1
    DISCONNECTED_FROM_SOMEWHERE = 2
    BAD_PASSWORD = 3
    BAD_PRIVATE_KEY = 4


# Create error subclass


class ErrorInContext1(Error[CodeInContext1, str]):
    @classmethod
    def create(cls, code: CodeInContext1, msg: str = "") -> ErrorInContext1:
        return cls(code=code, detail=msg)


# For convenience, create a type alias for Result with this error type

ResultInContext1 = Result[T, ErrorInContext1]

# Now we're ready to create an adapter for this context


class Context1Adapter(metaclass=abc.ABCMeta):
    def do_something(self) -> ResultInContext1[str]:
        raise NotImplementedError


# Let's create another error type for another context


class CodeInContext2(IntEnum):
    FAIL_TO_DO_SOMETHING_ELSE = 1
    DISCONNECTED_FROM_SOMEWHERE_ELSE = 2


class ErrorInContext2(Error[CodeInContext2, str]):
    @classmethod
    def create(cls, code: CodeInContext2, msg: str = "") -> ErrorInContext2:
        return cls(code=code, detail=msg)


ResultInContext2 = Result[T, ErrorInContext2]


class Context2Adapter(metaclass=abc.ABCMeta):
    def do_something_else(self, input_value: str) -> ResultInContext2[int]:
        raise NotImplementedError


# Now let's imagine that we have error for our domain


class DomainCode(IntEnum):
    RETRY_LATER = 0
    NOT_ENOUGH_MONEY = 1
    NOT_OLD_ENOUGH = 2
    NOT_ALLOWED = 3
    INTERNAL_ERROR = 4


class DomainError(Error[DomainCode, str]):
    @classmethod
    def err(cls: type[Self], code: DomainCode, msg: str = "") -> Err[t.Any, Self]:
        return Err(cls(code=code, detail=msg))


def some_condition(value: int) -> bool:
    return value > 18


@dataclass
class DomainService:
    adapter_1: Context1Adapter
    adapter_2: Context2Adapter

    def convert_error_from_context_1(
        self, error: ErrorInContext1
    ) -> Err[t.Any, DomainError]:
        if (
            error.code == CodeInContext1.BAD_PASSWORD
            or error.code == CodeInContext1.BAD_PRIVATE_KEY
        ):
            return DomainError.err(DomainCode.NOT_ALLOWED, "Bad credentials")
        elif (
            error.code == CodeInContext1.DISCONNECTED_FROM_SOMEWHERE
            or error.code == CodeInContext1.FAIL_TO_DO_SOMETHING
        ):
            return DomainError.err(DomainCode.RETRY_LATER, "Please try again later")
        # Checkout type annotation of error.code with your IDE
        assert_never(error.code)
        return DomainError.err(DomainCode.INTERNAL_ERROR)

    def convert_error_from_context_2(
        self, error: ErrorInContext2
    ) -> Err[t.Any, DomainError]:
        if error.code == CodeInContext2.DISCONNECTED_FROM_SOMEWHERE_ELSE:
            return DomainError.err(DomainCode.RETRY_LATER, "Please try again later")
        if error.code == CodeInContext2.FAIL_TO_DO_SOMETHING_ELSE:
            return DomainError.err(DomainCode.INTERNAL_ERROR)
        # Checkout type annotation of error.code with your IDE
        assert_never(error.code)
        return DomainError.err(DomainCode.INTERNAL_ERROR)

    def do_action(self) -> Result[int, DomainError]:
        result = self.adapter_1.do_something()
        if not result:
            return self.convert_error_from_context_1(result.value)

        result = self.adapter_2.do_something_else(result.value)
        if not result:
            return self.convert_error_from_context_2(result.value)

        if not some_condition(result.value):
            return DomainError.err(DomainCode.NOT_OLD_ENOUGH)

        return t.cast(Result[int, DomainError], result)


# Now, we can see that the result is a Result[int, DomainError].
# The callers of this notification service only need to handle errors from the domain.

# Moreover, we get an error anytime we propagate an error outside its context,
# I.E, the function signatures indicates that it returns an error from the domain
# so we must map errors from other contexts to errors from the domain.
# We can't mix errors from different contexts, which is a good thing.


@dataclass
class Usecase:
    service: DomainService

    def execute(self):
        """Execute the usecase.

        Type is inferred to be Result[int, DomainError].
        Usecase is completely unaware of the adapters, or the errors they can return.
        """
        result = self.service.do_action()
        if not result:
            return result

        return result


def main(adapter1: Context1Adapter, adapter2: Context2Adapter):
    service = DomainService(adapter1, adapter2)
    result = Usecase(service).execute()
    reveal_type(result)


# Much better, the code from the domain service is now very easy,
# and we can check that all possible errors are handled.

# Of course, this depends on the adapter implementations to be correct,
# but that always the case, regardless of exceptions or results.

# And we OWN those adapters, so we can make sure they are correct.
