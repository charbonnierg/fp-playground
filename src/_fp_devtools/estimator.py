from pprint import pformat


class CostEstimator:
    def __init__(self, overhead_µs: float, n_calls_per_sec: int):
        self.overhead_µs = overhead_µs
        self.n_calls_per_sec = n_calls_per_sec

    @property
    def overhead_µs_per_second(self) -> float:
        return self.overhead_µs * self.n_calls_per_sec

    @property
    def overhead_ms_per_minute(self) -> float:
        return self.overhead_μs_per_second * 60 / 1e3

    @property
    def overhead_ms_per_hour(self) -> float:
        return self.overhead_ms_per_minute * 60

    @property
    def overhead_second_per_day(self) -> float:
        return self.overhead_ms_per_minute * 60 * 24 / 1e3

    @property
    def overhead_minute_per_month(self) -> float:
        return self.overhead_µs_per_second * 3600 * 24 * 30 / 1e6 / 60

    @property
    def overhead_hour_per_year(self) -> float:
        return self.overhead_µs_per_second * 24 * 365 / 1e6

    def to_dict(self) -> dict[str, int | float]:
        return {
            "overhead_microsecond": self.overhead_µs,
            "n_calls_per_sec": self.n_calls_per_sec,
            "overhead_microsecond_per_second": self.overhead_µs_per_second,
            "overhead_millisecond_per_minute": self.overhead_ms_per_minute,
            "overhead_millisecond_per_hour": self.overhead_ms_per_hour,
            "overhead_second_per_day": self.overhead_second_per_day,
            "overhead_minute_per_month": self.overhead_minute_per_month,
            "overhead_hour_per_year": self.overhead_hour_per_year,
        }

    def __repr__(self) -> str:
        return pformat(
            self.to_dict(),
            sort_dicts=False,
            indent=2,
            underscore_numbers=True,
        )


def estimate_cost(
    overhead_µs: float,
    n_calls_per_sec: int,
) -> CostEstimator:
    """Estimate how much time will be spent on overhead per second, minute, hour, day, month, year,
    given the overhead per call and the number of calls per second."""
    return CostEstimator(overhead_µs, n_calls_per_sec)
