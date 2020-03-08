from pandas import DataFrame, Series, Index
from csv_file_upload import lazy_load_xform_save_csv, parameter_to_str, \
    get_dataframe_from_csv, save_dataframe_to_csv
from functional_tools.functor import functor


def filter_dataframe(df: DataFrame, filter_serie: Series) -> DataFrame:
    return DataFrame(df[filter_serie])


def read_csv_extract_extraordinary_save_csv(source_file: str,
                                            sink_file:str,
                                            target_column: str):
    def save_upload_dataframe_as_csv(df: DataFrame) -> None:
        save_dataframe_to_csv(df, sink_file)
    
    def filter_approved(df: DataFrame) -> DataFrame:
        return filter_dataframe(df, df[target_column] < 70)

    functor_filter_approved = lazy_load_xform_save_csv(get_dataframe_from_csv, 
                                                       functor(filter_approved), 
                                                       save_upload_dataframe_as_csv)
    functor_filter_approved(source_file)

def test_xform():
    def create_test_df(mock_file_source: str) -> DataFrame:
        return DataFrame([
            {'Matricula': 1111111, 'Nombre': 'A1', 'Final': 100},
            {'Matricula': 'XXX1112', 'Nombre': 'A2', 'Final': 90},
            {'Matricula': 113, 'Nombre': 'A3', 'Final': 80},
            {'Matricula': 1111114, 'Nombre': 'A1', 'Final': 70},
            {'Matricula': 1111115, 'Nombre': 'A1', 'Final': 60}
        ])

    def assert_result(df: DataFrame) -> None:
        assert len(df) == 1
        print('OK. Test Pass')

    def filter_approved(df: DataFrame) -> DataFrame:
        return filter_dataframe(df, df['Final'] < 70)
    
    functor_filter_approved = lazy_load_xform_save_csv(create_test_df,
                                                       functor(filter_approved),
                                                       assert_result)
    functor_filter_approved("Execute")


if __name__ == '__main__':
    import sys

    options = {True: lambda args: read_csv_extract_extraordinary_save_csv(
        parameter_to_str(args[1]), parameter_to_str(args[2]),
        parameter_to_str(args[3])),
               False: lambda _: test_xform()}
    action = options[len(sys.argv) > 1]
    action(sys.argv)
