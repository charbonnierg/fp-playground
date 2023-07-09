import pytest

from fp import Err, Ok, aio, bind, bind_err, fmap, fmap_err, pipe, visit, within_context
from tests.fp import fake


class TestMapFunc:
    def test_given_ok_result_when_map_then_apply_fn_to_result_value(self):
        fn = pipe(fmap(lambda x: x + 1))
        assert fn(Ok(1)) == Ok(2)

    def test_given_err_result_when_map_then_return_self(self):
        fn = pipe(fmap(fake.fail_if_called))
        assert fn(Err(1)) == Err(1)


class TestBindFunc:
    @pytest.mark.parametrize("result_type", [Ok, Err])
    def test_given_ok_result_when_bind_then_apply_fn_to_result_value_and_return_result(
        self, result_type: type[Ok | Err]
    ):
        fn = pipe(bind(lambda x: result_type(x + 1)))
        assert fn(Ok(1)) == result_type(2)

    def test_given_err_result_when_bind_then_return_self(self):
        fn = pipe(bind(fake.fail_if_called))
        assert fn(Err(1)) == Err(1)


class TestMapErrFunc:
    def test_given_ok_result_when_map_err_then_return_self(self):
        fn = pipe(fmap_err(fake.fail_if_called))
        assert fn(Ok(1)) == Ok(1)

    def test_given_err_result_when_map_err_then_apply_fn_to_result_value(self):
        fn = pipe(fmap_err(lambda x: x + 1))
        assert fn(Err(1)) == Err(2)


class TestBindErrFunc:
    def test_given_ok_result_when_bind_err_then_return_self(self):
        fn = pipe(bind_err(fake.fail_if_called))
        assert fn(Ok(1)) == Ok(1)

    @pytest.mark.parametrize("result_type", [Ok, Err])
    def test_given_err_result_when_bind_err_then_apply_fn_to_result_value_and_return_result(
        self, result_type: type[Ok | Err]
    ):
        fn = pipe(bind_err(lambda x: result_type(x + 1)))
        assert fn(Err(1)) == result_type(2)


class TestVisitFunc:
    @pytest.mark.parametrize("result_type", [Ok, Err])
    def test_given_result_when_visit_then_forward_result(
        self, result_type: type[Ok | Err]
    ):
        spy_called = "never called"

        def set_called(_value):
            nonlocal spy_called
            spy_called = _value

        fn = pipe(visit(lambda _: set_called(_)))
        assert fn(result_type(1)) == result_type(1)
        if result_type is Ok:
            assert spy_called == 1
        else:
            assert spy_called == "never called"


@pytest.mark.anyio
class TestWithinContextFunc:
    async def test_given_result_when_bind_context_then_execute_function_within_context_and_return_result(
        self,
    ):
        fn = pipe(fake.Context.create, bind(within_context(fake.Context.get_something)))
        assert fn(None) == Ok(1)
        assert fn("create") == Err("fail on create")
        assert fn("enter") == Err("fail on enter")
        assert fn("get") == Err("fail on get")

        async_fn = pipe(
            fake.Context.create,
            aio.bind(within_context(fake.Context.get_something_async)),
        )
        assert await async_fn(None) == Ok(1)
        assert await async_fn("create") == Err("fail on create")
        assert await async_fn("enter") == Err("fail on enter")
        assert await async_fn("get") == Err("fail on get")
