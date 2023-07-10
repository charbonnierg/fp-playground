from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import IntEnum

from typing_extensions import reveal_type

# Using IntEnum for code


class CodeInContext1(IntEnum):
    FAIL_TO_DO_SOMETHING = 1
    DISCONNECTED_FROM_SOMEWHERE = 2
    BAD_PASSWORD = 3
    BAD_PRIVATE_KEY = 4


# Create error subclass


class ErrorInContext1(Exception):
    def __init__(self, code: CodeInContext1, msg: str = "") -> None:
        self.code = code
        self.msg = msg
        super().__init__(msg)


class FailToDoSomethingError(ErrorInContext1):
    def __init__(self, msg: str = "") -> None:
        super().__init__(CodeInContext1.FAIL_TO_DO_SOMETHING, msg)


class DisconnectedFromSomewhereError(ErrorInContext1):
    def __init__(self, msg: str = "") -> None:
        super().__init__(CodeInContext1.DISCONNECTED_FROM_SOMEWHERE, msg)


class BadPasswordError(ErrorInContext1):
    def __init__(self, msg: str = "") -> None:
        super().__init__(CodeInContext1.BAD_PASSWORD, msg)


class BadPrivateKeyError(ErrorInContext1):
    def __init__(self, msg: str = "") -> None:
        super().__init__(CodeInContext1.BAD_PRIVATE_KEY, msg)


# Now we're ready to create an adapter for this context


class Context1Adapter(metaclass=abc.ABCMeta):
    def do_something(self) -> str:
        """Child classes must implement this function.

        Returns:
            a string
        Raises:
            ErrorInContext1: if something goes wrong.
        """
        raise NotImplementedError


# Let's create another error type for another context


class CodeInContext2(IntEnum):
    FAIL_TO_DO_SOMETHING_ELSE = 1
    DISCONNECTED_FROM_SOMEWHERE_ELSE = 2


class ErrorInContext2(Exception):
    def __init__(self, code: CodeInContext2, msg: str = "") -> None:
        self.code = code
        self.msg = msg
        super().__init__(msg)


class FailToDoSomethingElseError(ErrorInContext2):
    def __init__(self, msg: str = "") -> None:
        super().__init__(CodeInContext2.FAIL_TO_DO_SOMETHING_ELSE, msg)


class DisconnectedFromSomewhereElseError(ErrorInContext2):
    def __init__(self, msg: str = "") -> None:
        super().__init__(CodeInContext2.DISCONNECTED_FROM_SOMEWHERE_ELSE, msg)


class Context2Adapter(metaclass=abc.ABCMeta):
    def do_something_else(self, input_value: str) -> int:
        """Child classes must implement this function.

        Returns:
            an int
        Raises:
            ErrorInContext2: if something goes wrong.
        """
        raise NotImplementedError


# Now let's imagine that we have error for our domain


class DomainCode(IntEnum):
    RETRY_LATER = 0
    NOT_ENOUGH_MONEY = 1
    NOT_OLD_ENOUGH = 2
    NOT_ALLOWED = 3
    INTERNAL_ERROR = 4


class DomainError(Exception):
    def __init__(self, code: DomainCode, msg: str = "") -> None:
        self.code = code
        self.msg = msg


def some_condition(value: int) -> bool:
    return value > 18


@dataclass
class DomainService:
    adapter_1: Context1Adapter
    adapter_2: Context2Adapter

    def do_action(self):
        """Let's do it in a naive way, very close to what exception do
        in term of control flow."""
        try:
            string_value = self.adapter_1.do_something()
        except FailToDoSomethingError as exc:
            raise DomainError(DomainCode.RETRY_LATER) from exc
        except DisconnectedFromSomewhereError as exc:
            raise DomainError(DomainCode.RETRY_LATER) from exc
        except (BadPasswordError, BadPrivateKeyError) as exc:
            raise DomainError(DomainCode.NOT_ALLOWED) from exc
        except ErrorInContext1 as exc:
            raise DomainError(DomainCode.INTERNAL_ERROR, "unknown error") from exc

        try:
            result = self.adapter_2.do_something_else(string_value)
        except FailToDoSomethingElseError as exc:
            raise DomainError(DomainCode.INTERNAL_ERROR) from exc
        except DisconnectedFromSomewhereElseError as exc:
            raise DomainError(DomainCode.RETRY_LATER) from exc
        except ErrorInContext2 as exc:
            raise DomainError(DomainCode.INTERNAL_ERROR) from exc

        if not some_condition(result):
            raise DomainError(DomainCode.NOT_OLD_ENOUGH)
        return result


@dataclass
class Usecase:
    service: DomainService

    def execute(self):
        result = self.service.do_action()
        return result


# What's the problem here ?
# - Exceptions handling requires MUTUAL contract:
#    => Both the adapter implementation AND the caller must know about the exceptions.
#    => Unless exceptions are documented through docstrings, it is necessary to read the code
#       to know what exceptions can be raised. This is not a problem if the code is small,
#       but it is a problem if the code is big and a lot of different errors can occur.
#
# I'll try to emphasize this point:
#   => Handling error always requires to know about the error type (regardless of result or exception).
#      But, with exceptions in particular, the error type is never inferred, and must always be explicitely
#      catched using an except statement.
#      The only place to look for which exception catch is only explicit in the docstring, or in the code.
#      It's not possible to identify all possible errors.
#
# In our case if we look at type annotations:
def main(adapter1: Context1Adapter, adapter2: Context2Adapter):
    service = DomainService(adapter1, adapter2)
    result = Usecase(service).execute()
    reveal_type(result)


# By looking at the code, we can only see that the result is an int, without any information regarding the error.

# Also, exceptions need to be documented in EACH function they
# can be raised.
# In our case, it should be documented in DomainService.do_action() and in
# Uscase.execute().
#
# How can we improve this ?
