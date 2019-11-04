import pandas as pd
from src.utils.reactive import iter_to_observable, simple_print, unpack_iterrow_and_apply, print_data_iterrow, \
    do_reactive
from rx import operators as op
my_serie = pd.Series([1, 2, 3])
my_obs = iter_to_observable(my_serie)
my_obs.subscribe(simple_print)

# test list to stream to list
my_obs_from_list = iter_to_observable([4, 5, 6])
my_obs_from_list.\
    pipe(
    op.map(lambda x: x*2),
    op.to_iterable()).\
    subscribe(simple_print)

# test DF
base_dict= [{'id': 1, 'name': 'foo'}, {'id': 2, 'name': 'bar'}]
my_df = pd.DataFrame(base_dict)
my_obs_df = iter_to_observable(my_df.iterrows())
# print_iter = unpack_iterrow_and_apply(print_data_iterrow)
# print_id = unpack_iterrow_and_apply(lambda i, d: print(d.get('name')))
my_obs_df.pipe(op.map(lambda x: x[1].get('name'))).subscribe(simple_print)

do_reactive(my_df.iterrows(), simple_print, [op.map(lambda x: x[1].get('id') * 2)])
