import pytest

from fp import Err, Ok, aio, fmap
from fp.func_sync import fmap_err
from tests.fp import fake


@pytest.mark.anyio
class TestMap:
    async def test_given_ok_result_and_sync_fn_when_map_and_async_fn_then_apply_fn_to_result_value(
        self,
    ):
        fn = aio.pipe(aio.map(lambda x: x + 1))
        assert await fn(Ok(1)) == Ok(2)

    async def test_given_ok_result_and_async_fn_when_map_then_apply_fn_to_result_value(
        self,
    ):
        fn = aio.pipe(aio.map(fake.plus_one_async))
        assert await fn(Ok(1)) == Ok(2)

    async def test_given_err_result_and_sync_fn_when_map_then_return_self(self):
        fn = aio.pipe(aio.map(fake.fail_if_called))
        assert await fn(Err(1)) == Err(1)

    async def test_given_err_result_and_async_fn_when_map_then_return_self(self):
        fn = aio.pipe(aio.map(fake.async_fail_if_called))
        assert await fn(Err(1)) == Err(1)


@pytest.mark.anyio
class TestBind:
    @pytest.mark.parametrize("result_type", [Ok, Err])
    async def test_given_ok_result_and_sync_fn_when_bind_then_apply_fn_to_result_value_and_return_result(
        self, result_type: type[Ok | Err]
    ):
        fn = aio.pipe(aio.bind(lambda x: result_type(x + 1)))
        assert await fn(Ok(1)) == result_type(2)

    async def test_given_ok_result_and_async_fn_when_bind_then_apply_fn_to_result_value_and_return_result(
        self,
    ):
        fn = aio.pipe(aio.bind(fake.plus_one_async_ok))
        assert await fn(Ok(1)) == Ok(2)
        fn = aio.pipe(aio.bind(fake.plus_one_async_err))
        assert await fn(Ok(1)) == Err(2)

    async def test_given_err_result_and_sync_fn_when_bind_then_return_self(self):
        fn = aio.pipe(aio.bind(fake.fail_if_called))
        assert await fn(Err(1)) == Err(1)

    async def test_given_err_result_and_async_fn_when_bind_then_return_self(self):
        fn = aio.pipe(aio.bind(fake.async_fail_if_called))
        assert await fn(Err(1)) == Err(1)


@pytest.mark.anyio
class TestMapErr:
    async def test_given_ok_result_and_sync_fn_when_map_err_then_return_self(self):
        fn = aio.pipe(aio.map_err(fake.fail_if_called))
        assert await fn(Ok(1)) == Ok(1)

    async def test_given_ok_result_and_async_fn_when_map_err_then_return_self(self):
        fn = aio.pipe(aio.map_err(fake.async_fail_if_called))
        assert await fn(Ok(1)) == Ok(1)

    async def test_given_err_result_and_sync_fn_when_map_err_then_apply_fn_to_result_value(
        self,
    ):
        fn = aio.pipe(aio.map_err(lambda x: x + 1))
        assert await fn(Err(1)) == Err(2)

    async def test_given_err_result_and_async_fn_when_map_err_then_apply_fn_to_result_value(
        self,
    ):
        fn = aio.pipe(aio.map_err(fake.plus_one_async))
        assert await fn(Err(1)) == Err(2)


@pytest.mark.anyio
class TestBindErr:
    async def test_given_ok_result_and_sync_fn_when_bind_err_then_return_self(self):
        fn = aio.pipe(aio.bind_err(fake.fail_if_called))
        assert await fn(Ok(1)) == Ok(1)

    async def test_given_ok_result_and_async_fn_when_bind_err_then_return_self(self):
        fn = aio.pipe(aio.bind_err(fake.async_fail_if_called))
        assert await fn(Ok(1)) == Ok(1)

    async def test_given_err_result_and_sync_fn_when_bind_err_then_apply_fn_to_result_value_and_return_result(
        self,
    ):
        fn = aio.pipe(aio.bind_err(lambda x: Ok(x + 1)))
        assert await fn(Err(1)) == Ok(2)
        fn = aio.pipe(aio.bind_err(lambda x: Err(x + 1)))
        assert await fn(Err(1)) == Err(2)

    async def test_given_err_result_and_async_fn_when_bind_err_then_apply_fn_to_result_value_and_return_result(
        self,
    ):
        fn = aio.pipe(aio.bind_err(fake.plus_one_async_ok))
        assert await fn(Err(1)) == Ok(2)
        fn = aio.pipe(aio.bind_err(fake.plus_one_async_err))
        assert await fn(Err(1)) == Err(2)


@pytest.mark.anyio
class TestVisit:
    @pytest.mark.parametrize("result_type", [Ok, Err])
    async def test_given_result_and_sync_fn_when_visit_then_forward_result(
        self, result_type: type[Ok | Err]
    ):
        spy_called = "never called"

        def set_called(_value):
            nonlocal spy_called
            spy_called = _value

        fn = aio.pipe(aio.visit(lambda _: set_called(_)))
        assert await fn(result_type(1)) == result_type(1)
        if result_type is Ok:
            assert spy_called == 1
        else:
            assert spy_called == "never called"

    @pytest.mark.parametrize("result_type", [Ok, Err])
    async def test_given_result_and_async_fn_when_visit_then_forward_result(
        self, result_type: type[Ok | Err]
    ):
        spy_called = "never called"

        async def set_called_async(_value):
            nonlocal spy_called
            spy_called = _value

        fn = aio.pipe(aio.visit(set_called_async))
        assert await fn(result_type(1)) == result_type(1)
        if result_type is Ok:
            assert spy_called == 1
        else:
            assert spy_called == "never called"


@pytest.mark.anyio
class TestWithinContext:
    @pytest.mark.parametrize(
        "func",
        [
            aio.bind(aio.within_context(fake.Context.get_something)),
            aio.bind_within_context(fake.Context.get_something),
            aio.bind(aio.within_context(fake.Context.get_something_async)),
            aio.bind_within_context(fake.Context.get_something_async),
        ],
    )
    async def test_given_result_when_bind_context_then_execute_function_within_context_and_return_result(
        self, func
    ):
        fn = aio.pipe(
            fake.Context.create,
            func,
        )
        assert await fn(None) == Ok(1)
        assert await fn("get") == Err("fail on get")
        assert await fn("enter") == Err("fail on enter")
        assert await fn("create") == Err("fail on create")


@pytest.mark.anyio
class TestPipe:
    async def test_given_a_bunch_of_sync_and_async_functions_create_a_new_function(
        self,
    ):
        fn = aio.pipe(
            lambda x: Ok(x),
            aio.map(fake.plus_one_async),
            aio.bind(lambda x: Err[int, str](str(x))),
            fmap(lambda x: x + 1),
            fmap_err(lambda x: x + "a"),
        )
        assert await fn(0) == Err("1a")
