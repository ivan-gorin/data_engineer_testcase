import numpy as np
import pandas as pd


def gendf(CUSTOMER_NUM=5, PRODUCT_NUM=10, ORDER_NUM=10, MAX_TIME_OFFSET=1000):
    return pd.DataFrame({
        'customer_id': np.random.randint(0, CUSTOMER_NUM, size=(ORDER_NUM,)),
        'product_id': np.random.randint(0, PRODUCT_NUM, size=(ORDER_NUM,)),
        'timestamp': pd.Timestamp('2018-01-01 00:00:00') + pd.to_timedelta(np.random.randint(15, MAX_TIME_OFFSET, size=(ORDER_NUM,)), unit='s'),
        }).sort_values('timestamp')


def add_session_id(df):
    '''
    Add a session_id column to the dataframe.
    '''
    df['session_id'] = 0
    g = df.groupby('customer_id')
    offset = 0
    for _, group in g:
        df.loc[group.index, 'session_id'] = (group['timestamp'] - group['timestamp'].shift(1) > pd.Timedelta('3min')).fillna(0).cumsum() + offset
        offset = df['session_id'].max() + 1


if __name__ == '__main__':
    df = gendf()
    add_session_id(df)
    print(df.sort_values('customer_id'))
