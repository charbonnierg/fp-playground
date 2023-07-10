from __future__ import annotations

import abc
import typing as t


class CodeProtocol(t.Protocol):
    @property
    def name(self) -> str:  # pragma: no cover
        ...

    @property
    def value(self) -> int:  # pragma: no cover
        ...


CodeT = t.TypeVar("CodeT", covariant=True, bound=CodeProtocol)
DetailT = t.TypeVar("DetailT", covariant=True)


class Error(t.Generic[CodeT, DetailT], metaclass=abc.ABCMeta):
    def __init__(
        self,
        code: CodeT,
        detail: DetailT,
    ) -> None:
        self.code = code
        self.detail = detail

    def __repr__(self) -> str:
        maybe_msg = "" if not self.detail else f", detail={repr(self.detail)}"
        return f"{self.__class__.__name__}(code={self.code.value}, code_name={repr(self.code.name)}{maybe_msg})"
