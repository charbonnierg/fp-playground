from __future__ import annotations

import abc
import typing as t
from dataclasses import dataclass
from enum import IntEnum

from typing_extensions import Self, reveal_type

from fp import Result
from fp.result import Err
from fp.struct.error import Error

T = t.TypeVar("T")

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

    def do_action(self):
        result = self.adapter_1.do_something()
        if not result:
            return result

        result = self.adapter_2.do_something_else(result.value)
        if not result:
            return result

        if not some_condition(result.value):
            return DomainError.err(DomainCode.NOT_OLD_ENOUGH)

        return t.cast(Result[int, DomainError], result)


@dataclass
class Usecase:
    service: DomainService

    def execute(self):
        result = self.service.do_action()
        if not result:
            return result

        return result


def main(adapter1: Context1Adapter, adapter2: Context2Adapter):
    service = DomainService(adapter1, adapter2)
    result = Usecase(service).execute()
    reveal_type(result)


# We can see (although it takes a bit of time to get familiar with annotations)
# that the result is a Result[T, Error[CodeInContext1 | CodeInContext2 | DomainCode, str]].

# So we know that we need to handle all these errors (errors from context1, errors from context2, errors from the domain.)

# IMO, centralizing error handling for errors coming from different contexts goes against
# the principle of separation of concern, and makes it difficult to draw clear boundaries
# between contexts.

# This example was meant to show that event though result objects can
# be composed, it's not always a good idea to do so without care.

# This is the same thing with exceptions ! If exceptions are not catched,
# they are being raised until they are catched by a function in parent scope,
# and if they are not catched, the program exits.

# Be it exceptions or results, it's important to handle them at the right place.

# Appendice: Why don't we use the same errors for domain, context1 and context2 ?
# (just like we do in QUARA, where our adapters raises errors understood
#  within the domain, and not errors understood within the context of the adapter)
# e.g: OperationFailedError, OperationConflictError, ...

# The reason is that if we want to share some ports between different contexts,
# (for example: `PubsubGateway`, `PaymentGateway`, `EmailGateway`, ...)
# we don't want to have to import errors from other contexts.

# PubsubGateway should throw (I use throw to avoid distinction between result
# or exception, because it does not matter) errors understood within its domain
# just like PaymentGateway should throw errors understood within its domain.

# It should be up to each domain service, or secondary adapter to translate
# errors from other contexts to errors understood within its domain.
# (again: regardless whether errors are exceptions or results)

# Next objective: Can we rely on developer tools to help us with this translation ?
# (e.g: IDE, linters, mypy, ...)
