from __future__ import annotations

from . import fn_async as aio
from .__about__ import __version__
from .fn_sync import bind, bind_err, fmap, fmap_err, pipe, visit, within_context
from .promise import Promise
from .result import Err, Ok, Result
from .writer import WErr, WOk, WResult

__all__ = [
    "__version__",
    "aio",
    "fmap",
    "fmap_err",
    "bind",
    "bind_err",
    "visit",
    "within_context",
    "pipe",
    "Ok",
    "Err",
    "Result",
    "Promise",
    "WOk",
    "WErr",
    "WResult",
]
