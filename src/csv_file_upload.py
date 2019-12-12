#!/usr/bin/env python3
from pandas import DataFrame, read_csv, concat
from functional_tools.functor import functor
from typing import Callable, Dict, Any, Optional


def get_dataframe(get_fn: Callable[[str], DataFrame], filename: str) -> DataFrame:
    return get_fn(filename)


def get_dataframe_from_csv(filename: str) -> DataFrame:
    def _read_csv(filename: str):
        return read_csv(filename, sep=',')
    return get_dataframe(_read_csv, filename)


def save_dataframe_to_csv(df: DataFrame, path_to_save: str) -> None:
    print(path_to_save)
    print(df)
    df.to_csv(path_to_save, sep=',', encoding='utf-8', index=False)


def rename_columns(base_df: DataFrame, column_name_map: Dict[str, str]) -> DataFrame:
    return DataFrame(base_df[:, column_name_map.keys()], columns=column_name_map.values())


def last_n_digits_from_str(base_value: any, n: int) -> str:
    base_str = str(base_value)
    return base_str[max(0, len(base_str)-n):len(base_str)]


def apply_fn_to_column(base_df: DataFrame, column_name: str,
                       fn_to_apply: Callable[[Any], Any]) -> Any:
    modified_col = DataFrame(base_df[column_name].map(fn_to_apply), columns=[column_name])
    other_columns = list(set(base_df.columns)-set([column_name]))
    return DataFrame(data=concat([modified_col, base_df.loc[:, other_columns]], axis=1,
                                 ignore_index=False),
                     columns=base_df.columns)


def show_last_n_digits_of_column(base_df: DataFrame, column_name: str, digits: int) -> DataFrame:
    def _last_n_digits_from_str(base_str: str):
        return last_n_digits_from_str(base_str, digits)
    return apply_fn_to_column(base_df, column_name, _last_n_digits_from_str)


def lazy_load_xform_save_csv(load_fn: Callable[[str], DataFrame],
                             save_fn: Callable[[DataFrame], None],
                             xform_fn: Callable[[DataFrame], DataFrame]) -> functor:
    return functor(load_fn).\
        map(xform_fn).\
        map(save_fn)


def test_xform():
    def create_test_df(mock_file_source: str) -> DataFrame:
        return DataFrame([
            {'Matricula': 1111111, 'Nombre': 'A1', 'Final': 10},
            {'Matricula': 'XXX1112', 'Nombre': 'A2', 'Final': 9},
            {'Matricula': 113, 'Nombre': 'A3', 'Final': 8}
        ])

    def assert_result(df: DataFrame) -> None:
        expected = DataFrame([
            {'Matricula': '1111', 'Nombre': 'A1', 'Final': 10},
            {'Matricula': '1112', 'Nombre': 'A2', 'Final': 9},
            {'Matricula': '113', 'Nombre': 'A3', 'Final': 8}
        ])
        assert df.equals(expected)
        print('OK. Test Pass')

    def show_last_4_digits_from_matricula(df: DataFrame) -> DataFrame:
        return show_last_n_digits_of_column(df, 'Matricula', 4)

    functor_read_df_modify_mat_save_csv =  \
        lazy_load_xform_save_csv(create_test_df,
                                 assert_result,
                                 show_last_4_digits_from_matricula)
    functor_read_df_modify_mat_save_csv('now do your work')

def parameter_to_str(parameter: Optional[Any]) -> str:
    return str(parameter) if parameter is not None else ""


if __name__ == '__main__':
    def read_csv_remove_char_matricula_save_csv(source_file: str,
                                                sink_file: str,
                                                xform_col:str,
                                                final_columns:str):
        def show_last_4_digits_from_matricula(df: DataFrame) -> DataFrame:
            return show_last_n_digits_of_column(df, xform_col, 4)

        def save_upload_dataframe_as_csv(df: DataFrame) -> None:
            return save_dataframe_to_csv(df, sink_file)

        def choose_columns(df: DataFrame) -> DataFrame:
            col_list = final_columns.split(',',-1)
            return DataFrame(df.loc[:,col_list], columns=col_list)

        functor_read_df_modify_mat_save_csv =  \
            lazy_load_xform_save_csv(get_dataframe_from_csv,
                                     save_upload_dataframe_as_csv,
                                     functor(show_last_4_digits_from_matricula).map(choose_columns))
        functor_read_df_modify_mat_save_csv(source_file)

    import sys

    options = { True: lambda args: read_csv_remove_char_matricula_save_csv(
        parameter_to_str(args[1]), parameter_to_str(args[2]),
        parameter_to_str(args[3]), parameter_to_str(args[4])),
                False: lambda _: test_xform()}
    action = options[len(sys.argv) > 1]
    action(sys.argv)
