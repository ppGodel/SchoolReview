#!/usr/bin/env python3
from typing import Callable, Dict, List, Optional, Any
import json
from functools import reduce
from functional_tools.functor import functor

def create_base_df(mock_file_source: str) -> Dict[str, str]:
    return {mock_file_source: mock_file_source}

def merge_dicts(d1: Dict, d2: Dict) -> Dict:
    return {**d1, **d2}

def get_dicts(list_dict: List[str], dict_getter_from_str: Callable[[str], Dict]):
    dict_list = map(dict_getter_from_str, list_dict)
    return reduce(merge_dicts, dict_list)

def get_functor_dict(list_dict: List[Dict], dict_getter_from_str: Callable[[str], Dict]) \
    -> functor:
    return functor.of(list_dict).map(lambda list_str: map(dict_getter_from_str, list_str))\
                                .map(lambda list_dict: reduce(merge_dicts, list_dict))

def get_dict_from_file(file_name: str) -> Dict:
    with open(file_name) as json_file:
        data = json.load(json_file)
    return data

def compare_dicts(base_dicts: List[str], dicts_for_compare: List[str]) -> None:
    d_1 = get_functor_dict(base_dicts, get_dict_from_file)()
    d_2 = get_functor_dict(dicts_for_compare, get_dict_from_file)()
    assert d_1 == d_2
    print("Dicts are identical")

def test_dicts() -> None:
    base_df = ["path1", "path2", "path3"]
    expected = {'path1': 'path1', 'path2': 'path2', 'path3': 'path3'}
    functor_dict = get_functor_dict(base_df, create_base_df)
    d_1 = functor_dict() # executing the code :D
    assert d_1 == expected
    print('Tests ok')

def parameter_to_str(parameter: Optional[Any]) -> str:
    return str(parameter) if parameter is not None else ""

def call_compare(args: List[str]) -> None:
    compare_dicts(parameter_to_str(args[1]).split(","), parameter_to_str(args[2]).split(","))

def call_test(_: List[str]) -> None:
    test_dicts()

if __name__ == '__main__':

    import sys

    options = {True: call_compare,
               False: call_test}
    action = options[len(sys.argv) > 1]
    action(sys.argv)
