from enum import IntEnum

from fp_extras.error import Error


class CodeForTests(IntEnum):
    UNKNOWN = 0
    FAKE = 1


class TestErrorFactory:
    def test_create_error(self):
        err = Error(CodeForTests.FAKE, "some error message")
        assert err.code == CodeForTests.FAKE
        assert err.detail == "some error message"
        assert (
            repr(err) == "Error(code=1, code_name='FAKE', detail='some error message')"
        )
