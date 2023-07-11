"""WARNING: This module contains INVALID code.

Do not copy/paste content from it if you plan to use it !!!
"""
from fp_extras.error import Error

# We expect an error because code does not implement the Code protocol
Error(code=1, detail="test error")  # type: ignore

# We expect an error because code does not implement the Code protocol
Error(code="test", detail="test error")  # type: ignore


# We expect an error because int does not implement the Code protocol
class MyError(Error[int]):  # type: ignore
    pass


# Let's try with a valid implementation
class MyCode:
    @property
    def name(self) -> str:
        return "STATIC"

    @property
    def value(self) -> int:
        return 0


class StaticError(Error[MyCode, str]):
    pass
