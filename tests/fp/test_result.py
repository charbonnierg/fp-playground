import pytest

from fp import Err, Ok


@pytest.mark.parametrize("value", [None, 1, "1", True, False, 1.0, 1j, object()])
class TestResultFactory:
    def test_given_value_then_create_ok_with_value(self, value: object):
        result = Ok(value)
        assert result.value == value

    def test_given_value_then_create_err_with_value(self, value: object):
        result = Err(value)
        assert result.value == value


@pytest.mark.parametrize("value", [None, 1, "1", True, False, 1.0, 1j, object()])
class TestResultStringRepresentation:
    def test_ok_str_repr(self, value: object):
        assert repr(Ok(value)) == f"Ok({repr(value)})"

    def test_err_str_repr(self, value: object):
        assert repr(Err(value)) == f"Err({repr(value)})"


@pytest.mark.parametrize("value", [None, 1, "1", True, False, 1.0, 1j, object()])
class TestResultDunder:
    def test_given_result_is_err_when_bool_then_return_false(self, value: object):
        result = Err(value)
        assert bool(result) is False

    def test_given_result_is_ok_when_bool_then_return_true(self, value: object):
        result = Ok(value)
        assert bool(result) is True

    def test_given_ok_and_err_with_same_value_then_equal_is_false(self, value: object):
        assert Ok(value) != Err(value)


class TestOkMethods:
    def test_given_ok_when_map_then_apply_fn_to_value(self):
        result = Ok(1).map(lambda x: x + 1)
        assert result == Ok(2)

    def test_given_ok_when_bind_then_apply_fn_to_value_and_return_result(self):
        result = Ok(1).bind(lambda x: Ok(x + 1))
        assert result == Ok(2)

    def test_given_ok_when_map_err_then_return_self(self):
        result = Ok(1).map_err(lambda x: x + 1)
        assert result == Ok(1)

    def test_given_ok_when_bind_err_then_return_self(self):
        result = Ok(1).bind_err(lambda x: Err(x + 1))
        assert result == Ok(1)


class TestErrMethods:
    def test_given_err_when_map_then_return_self(self):
        result = Err(1).map(lambda x: x + 1)
        assert result == Err(1)

    def test_given_err_when_bind_then_return_self(self):
        result = Err(1).bind(lambda x: Ok(x + 1))
        assert result == Err(1)

    def test_given_err_when_map_err_then_apply_fn_to_value(self):
        result = Err(1).map_err(lambda x: x + 1)
        assert result == Err(2)

    def test_given_err_when_bind_err_then_apply_fn_to_value_and_return_result(self):
        result = Err(1).bind_err(lambda x: Err(x + 1))
        assert result == Err(2)
