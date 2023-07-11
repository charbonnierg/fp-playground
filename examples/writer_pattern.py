"""
OBJECTIVES:

Write code which can generate log messages and telemetry data using
pure functions only.

MOTIVATION:

Test easily, and separate concerns (e.g, how to publish metrics and logs is completely
unrelated to WHY we create them in the first place.)
"""
from __future__ import annotations

import abc
import typing as t
from dataclasses import astuple, dataclass, field

from _fp._func_types import L, R
from fp import WErr, WOk, WResult

ValueT = t.TypeVar("ValueT", int, float)


@dataclass
class Labels(metaclass=abc.ABCMeta):
    """A base class for labels."""

    pass


LabelsT = t.TypeVar("LabelsT", bound=Labels)


@dataclass
class Metric(t.Generic[LabelsT, ValueT]):
    name: str
    labels: type[LabelsT]
    type: type[ValueT]


@dataclass
class MetricObservation(t.Generic[LabelsT, ValueT]):
    """A class used to observe metrics."""

    metric: Metric[LabelsT, ValueT]
    labels: tuple[str, ...]
    value: int | float


@dataclass
class LogEntry:
    """A class used to create log messages."""

    level: t.Literal["DEBUG", "INFO", "WARN", "ERROR"]
    msg: str
    kwargs: dict[str, t.Any] = field(default_factory=dict)


@dataclass
class TelemetryEntry:
    """A container for telemetry data."""

    logs: list[LogEntry] = field(default_factory=list)
    metrics: list[MetricObservation[t.Any, t.Any]] = field(default_factory=list)


# Create a type alias for result objects that include telemetry data.
ResultWithTelemetry = WResult[L, R, TelemetryEntry]
OkWithTelemetry = WOk[L, R, TelemetryEntry]
ErrWithTelemetry = WErr[L, R, TelemetryEntry]
# Now it's very easy to write pure functions that return a result with telemetry data.


# Some helper functions


def metric(
    metric: Metric[LabelsT, ValueT],
    labels: LabelsT,
    value: ValueT,
) -> MetricObservation[LabelsT, ValueT]:
    """Create a new metric observation. Labels must be provided as dataclass objects."""
    return MetricObservation(metric, astuple(labels), value)


def log(
    level: t.Literal["DEBUG", "INFO", "WARN", "ERROR"],
    msg: str,
    **kwargs: t.Any,
) -> LogEntry:
    """Create a new log message."""
    return LogEntry(level, msg, kwargs)


def emit(*items: LogEntry | MetricObservation[t.Any, t.Any]) -> TelemetryEntry:
    """Create a telemetry entry from a list of items."""
    logs = [item for item in items if isinstance(item, LogEntry)]
    metrics = [item for item in items if isinstance(item, MetricObservation)]
    return TelemetryEntry(logs, metrics)


# Application code


@dataclass
class CustomLabels(Labels):
    service: str
    version: str


CUSTOM_METRIC = Metric("test", CustomLabels, type=int)


def some_instrumented_function(input_value: bool) -> ResultWithTelemetry[int, str]:
    if not input_value:
        return WErr(
            "NOT OK",
            emit(
                log("ERROR", "Input value was false."),
                metric(CUSTOM_METRIC, CustomLabels("test", "1.0"), 1),
            ),
        )
    # On happy path we do not log, nor we update metric
    return WOk(42)


# Recommendation: use `WResult` as a return type for functions that can fail.
# Only primary adapters are responsible for "flushing" the WResult using a function
# but usecases, or secondary adapters which emit logs or metrics should return WResult.
# We don't care that much about the performance of the telemetry data, so we can
# use a simple tuple to store the telemetry data, and append it until it's flushed
# It logs are pushed with 300ms of delay (i.e, after a usecase fully executes),
# it's no big deal !


class HTTPResponse:
    def __init__(self, *args: t.Any):
        pass


# Get an HTTP response, after executing a function which:
# - may fail with a string or return a success of integer
# - may produce logs
# - may produce metrics
# And everything is a pure function, there is no side effect.
res = (
    some_instrumented_function(True)  # Get a result which is either Ok[int] or Err[str]
    .map(
        # Transform value contained in OK result or forward Err result
        lambda ok: HTTPResponse(200)
    )
    .rescue(
        # Transform Err result value into an Ok value or forward Ok result
        lambda err: HTTPResponse(500)
    )
    .flush(
        # Drop telemetry data after processing it and forward result
        lambda telemetry: print(telemetry)
    )
    .unwrap()  # Drop the result object and get the value contained within it
)

# Function calls are still composable, we can mix async or sync functions
# with a little bit of work on the framework side, but it's definitely doable,
# and very testable (and if we design a good framework API, it should not change over time)
# I think it's a good way to separate concerns, and it's very easy to test.
