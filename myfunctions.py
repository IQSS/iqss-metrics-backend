from datetime import datetime

import pandas as pd


# get date from variable  and return date-type.
# this is mainly used for the Google TimeStamp of the Forms.
def convert_timestamp_dt(timestamp_string):
    return datetime.strptime(timestamp_string, "%m/%d/%Y %H:%M:%S").date()


# get data from variable and return formatted string
def convert_timestamp_str(timestamp_string):
    return str(datetime.strptime(timestamp_string, "%m/%d/%Y %H:%M:%S").date())

# return the last 12 rows, not including last one
# used after aggregation and exclude current month, which is not complete
def df_previous_12_months(df):
    if len(df) < 12:
        return df
    else:
        return df.head(len(df) - 1).tail(12)


# return date type of the current month
# if it is Jun 19 2020 now, it returns Jun 1 2020 midnight
# Timestamp('2020-06-01 00:00:00')
def get_beginning_of_this_month():
    t = datetime.now()
    return pd.Timestamp(datetime(t.year, t.month, 1, 0, 0, 0, 0))


# returns the start of the current month, but one year before
# if it is Jun 19 2020 now, it returns Jun 1 2019 midnight
# Timestamp('2019-06-01 00:00:00')
def get_last_year():
    t = datetime.now()
    return pd.Timestamp(datetime(t.year - 1, t.month, 1, 0, 0, 0, 0))

# return the current year in string format:
# '2020'
def get_current_year_str():
    return str(datetime.now().year)


# fiters the records of the data frame of the last 12 months.
def filter_last_12_months(df, field, drop_datetime=False):
    df2 = df.copy()
    df2["datetime"] = df2[field].transform(lambda x: pd.Timestamp(x))
    df3 = df2[(df2['datetime'] >= get_last_year()) & (df2['datetime'] < get_beginning_of_this_month())]

    if drop_datetime:
        del df3['datetime']

    return df3


# return the start datetime of this year
# if it is Jun 19 2020 now, it returns Jan 1 2020 midnight
# Timestamp('2020-01-01 00:00:00')
def get_beginning_of_this_year():
    t = datetime.now()
    return pd.Timestamp(datetime(t.year, 1, 1, 0, 0, 0, 0))


# return the records from the start of this year
def get_records_YTD(df, field="Timestamp", drop_datetime=False):
    df2 = df.copy()
    df2["datetime"] = df2[field].transform(lambda x: pd.Timestamp(x))
    df3 = df2[df2['datetime'] >= get_beginning_of_this_year()]

    if drop_datetime:
        del df3['datetime']

    return df3
