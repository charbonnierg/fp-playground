# Read before browsing code

> Disclaimer: This example relies on the assumption that it's OK for several projects to rely on the same adapter ports (for example, all our projects could use the same `PubsubGateway` in order to send notifications). Each project, or at least each bounded context, should however abstract the usage of the `PubsubGateway` through a Domain Service. Each project is free to bring its own `PubsubAdapter` to work with the `PubsubGateway`, or some maintained adapters could be shared accross projects (`NatsPubsubAdapter`, `InMemoryPubsubAdapter`, ...).

> The encapsulation flow is:
> *Usecase* > *Domain Service* > *Port (ex: `PubsubGateway`)* > *Adapter (ex: `NatsPubsubAdapter`)* > *Third-party code (ex: `nats-py`)*

> Finally, each of those adapter port should have its own set of errors, understood within its context (e.g: `PubsubGateway` throws a finit set of errors, which is distinct from the finite set of errors throwned by `EmailGateway`).


There are three implementations of the same business logic:

- [custom_errors_with_exceptions.py](./custom_errors_with_exceptions.py)

- [custom_errors_with_results_01_imperative.py](./custom_errors_with_results_01_imperative.py)

- [custom_errors_with_results_02_imperative_error_translation.py](./custom_errors_with_results_02_imperative_error_translation)

- [custom_errors_with_results_03_functional_programming.py](custom_errors_with_results_03_functional_programming.py)

> Note: there are also files ending with `__wc.py` (stands for "without comment") which are used to count compare line length without comments.

Each script defines:

- two adapters interfaces
- one domain service which uses those adapter interfaces
- one usecase which calls the domain service

The objective is to identify which strategy should be preferred to communicate and handle errors.

# Read after browsing code

## Comparative

| Pattern | Error type enforced  | Error Type inspectable | Error Type Inferred | Exhaustive error handling |
|----|---|---|---|--|
|  | Can developer tools be used to enforce type or error that a function should throw (e.g, adapter contract) ? | Is it possible for errors to have specific types inspectable at runtime ? | Can developer tools be used to infer error types which can be throwned by a function (e.g, caller contract) | Can developer tools be used to enforce that all error types which can be throwed by a function are handled ? 
| `Exceptions` | ❌ |  ✅  | ❌ | ❌
| `Result` | ✅ | ✅ | ✅ | ✅