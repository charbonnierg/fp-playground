import pytest

from fp.promise import Err, Ok, Promise
from tests.fp import fake


@pytest.mark.anyio
class TestPromiseFactory:
    async def test_given_coroutine_returning_result_create_promise(self):
        promise = Promise(fake.coro_returns_ok())
        assert await promise == Ok(1)

    async def test_given_coroutine_returning_ok_value_create_promise(self):
        promise = Promise.of_ok(fake.coro_returns_value())
        assert await promise == Ok(1)

    async def test_given_coroutine_returning_err_value_create_promise(self):
        promise = Promise.of_err(fake.coro_returns_value())
        assert await promise == Err(1)


@pytest.mark.anyio
class TestPromiseOkMethods:
    async def test_given_ok_and_sync_fn_when_map_then_apply_fn_to_awaited_result_value(
        self,
    ):
        promise = Promise.of_ok(fake.coro_returns_value()).map(lambda x: x + 1)
        assert await promise == Ok(2)

    async def test_given_ok_and_async_fn_when_map_then_apply_fn_to_awaited_result_value(
        self,
    ):
        promise = Promise.of_ok(fake.coro_returns_value()).map(fake.plus_one_async)
        assert await promise == Ok(2)

    async def test_given_ok_and_sync_fn_when_bind_then_apply_fn_to_awaited_result_value_and_return_result(
        self,
    ):
        promise = Promise.of_ok(fake.coro_returns_value()).bind(lambda x: Ok(x + 1))
        assert await promise == Ok(2)

    async def test_given_ok_and_async_fn_when_bind_then_apply_fn_to_awaited_result_value_and_return_result(
        self,
    ):
        promise = Promise.of_ok(fake.coro_returns_value()).bind(fake.plus_one_async_ok)
        assert await promise == Ok(2)

    async def test_given_ok_and_sync_fn_when_map_err_then_return_awaited_result(self):
        promise = Promise.of_ok(fake.coro_returns_value()).map_err(fake.fail_if_called)
        assert await promise == Ok(1)

    async def test_given_ok_and_async_fn_when_map_err_then_return_awaited_result(self):
        promise = Promise.of_ok(fake.coro_returns_value()).map_err(
            fake.async_fail_if_called
        )
        assert await promise == Ok(1)

    async def test_given_ok_and_sync_fn_when_bind_err_then_return_awaited_result(
        self,
    ):
        promise = Promise.of_ok(fake.coro_returns_value()).bind_err(fake.fail_if_called)
        assert await promise == Ok(1)

    async def test_given_ok_and_async_fn_when_bind_err_then_return_awaited_result(
        self,
    ):
        promise = Promise.of_ok(fake.coro_returns_value()).bind_err(fake.fail_if_called)
        assert await promise == Ok(1)


@pytest.mark.anyio
class TestPromiseErrMethods:
    async def test_given_err_and_sync_fn_when_map_then_return_awaited_result(self):
        promise = Promise.of_err(fake.coro_returns_value()).map(fake.fail_if_called)
        assert await promise == Err(1)

    async def test_given_err_and_async_fn_when_map_then_return_awaited_result(self):
        promise = Promise.of_err(fake.coro_returns_value()).map(
            fake.async_fail_if_called
        )
        assert await promise == Err(1)

    async def test_given_err_and_sync_fn_when_bind_then_return_awaited_result(self):
        promise = Promise.of_err(fake.coro_returns_value()).bind(fake.fail_if_called)
        assert await promise == Err(1)

    async def test_given_err_and_async_fn_when_bind_then_return_awaited_result(self):
        promise = Promise.of_err(fake.coro_returns_value()).bind(
            fake.async_fail_if_called
        )
        assert await promise == Err(1)

    async def test_given_err_and_sync_fn_when_map_err_then_apply_fn_to_awaited_result_value(
        self,
    ):
        promise = Promise.of_err(fake.coro_returns_value()).map_err(lambda x: x + 1)
        assert await promise == Err(2)

    async def test_given_err_and_async_fn_when_map_err_then_apply_fn_to_awaited_result_value(
        self,
    ):
        promise = Promise.of_err(fake.coro_returns_value()).map_err(fake.plus_one_async)
        assert await promise == Err(2)

    async def test_given_err_and_sync_fn_when_bind_err_then_apply_fn_to_awaited_result_value_and_return_result(
        self,
    ):
        promise = Promise.of_err(fake.coro_returns_value()).bind_err(
            lambda x: Err(x + 1)
        )
        assert await promise == Err(2)

    async def test_given_err_and_async_fn_when_bind_err_then_apply_fn_to_awaited_result_value_and_return_result(
        self,
    ):
        promise = Promise.of_err(fake.coro_returns_value()).bind_err(
            fake.plus_one_async_err
        )
        assert await promise == Err(2)
