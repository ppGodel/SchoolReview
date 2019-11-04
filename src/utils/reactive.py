from typing import Any, Tuple, Callable, Iterable, List
import rx
from rx import operators as op
import pandas as pd


def simple_print(x: Any) -> None:
    print(x)


def print_data_iterrow(indx: pd.MultiIndex, data: pd.Series) -> None:
    print(data)


def unpack_iterrow_and_apply(fn: Callable[[pd.MultiIndex, pd.Series], Any]) -> Any:
    def apply_fn(x: Tuple[pd.MultiIndex, pd.Series]):
        indx, data = x
        return fn(indx, data)
    return apply_fn


def iter_to_observable(iter: Iterable[Any]) -> rx.Observable:
    return rx.from_(iter)


def do_reactive(iter: Iterable[Any], consumer: Callable[[Any], Any],
                operations: List[Callable[[rx.Observable], Any]]):
    obs = iter_to_observable(iter)
    obs.pipe(*operations).subscribe(consumer)