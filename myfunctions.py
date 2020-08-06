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


def get_beginning_of_this_year():
    """
    return the start datetime of this year
    if it is Jun 19 2020 now, it returns Jan 1 2020 midnight
    Timestamp('2020-01-01 00:00:00')
    :return: pandas Timestamp
    """
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


def get_counts(df, column):
    """
    get the total for a column and return a cleaned up datafram
    :param df: input datafram
    :param column: columnt to calculate the counts of
    :return: new dataframe
    """
    df2 = pd.DataFrame({'count': df[column].value_counts()}).reset_index()
    df2.rename(columns={'index': column}, inplace='True')
    return df2


def create_other_category(df, cut_off=0.05):
    """
    Creates an 'Other" category with the drop off value
    Functions is used in combinations with create percentage and counts.
    So we have first column, count and fraction column. (else sum will not work)

    :param df: input dataframe
    :param cut_off: cut-off value
    :return:
    """
    x = {}
    for idx, c in enumerate(df.columns):
        if idx == 0:
            x[c] = "Other"
        else:
            x[c] = df[df.fraction < cut_off][c].sum()
    new_df = pd.DataFrame(x, index=[0])
    df = df[df.fraction >= cut_off]
    df = df.append(new_df)

    return df


def create_percentage(df, column, cut_off=0.05):
    """
    Creates a percentage column.
    :param df: input dataframe
    :param column: column to calculate the percentage of the total of
    :param cutoff: sum percentage lower than cutoff to one group
    :return: dataframe with fraction and percentage
    """
    total = df[column].sum()
    df["fraction"] = round(df[column] / total, ndigits=2)
    if cut_off > 0.:
        df = create_other_category(df, cut_off)
    df["percentage"] = df["fraction"].transform(lambda x: f"{round(x * 100)}%")
    return df


# --------------- for CSS

def last_FY(df, column):
    """

    :param df: dataframe input
    :param column: column name with the FYxy values
    :return: highest FY value in the column
    """
    df_year = df.apply(lambda row: row[column][2:4], axis=1)
    last_FY = f"FY{df_year.unique().max()}"
    return last_FY


# NOTE This function does the same thing as create_percentage()...
def combine_lower_n_percent(df, column, threshold=5, decimals=0):
    df = df.sort_values(column, ascending=False)
    total = df[column].sum()
    df["percentage"] = 100.0 * df[column] / total

    other = df[df["percentage"] < threshold][column].sum()

    # keep
    df = df[df["percentage"] >= threshold]
    other = pd.DataFrame({column: other, "percentage": 100 * other / total}, index=["Other"])
    df = df.append(other)
    if decimals > 0:
        df["percentage"] = df.apply(lambda row: round(row["percentage"], decimals), axis=1)
    elif decimals == 0:
        df["percentage"] = df.apply(lambda row: round(row["percentage"]), axis=1)

    return df


# ----------------
def combine_lower_n_percent_complete(df, column, other_cols=[], sum_columns=[], threshold=5, decimals=0):
    df = df.sort_values(column, ascending=False)
    total = df[column].sum()
    df["percentage"] = 100.0 * df[column] / total

    other = df[df["percentage"] < threshold][column].sum()

    x = {"percentage": 100 * other / total, column: df[df["percentage"] < threshold][column].sum()}

    for c in sum_columns:  # calc the sums
        x[c] = df[df["percentage"] < threshold][c].sum()

    # keep
    df = df[df["percentage"] >= threshold]
    if not other_cols:  # use index
        other = pd.DataFrame({column: other, "percentage": 100 * other / total}, index=["Other"])
    else:  # use columns
        for c in other_cols:
            x[c] = ["Other"]
        other = pd.DataFrame(x)

    df = df.append(other)
    if decimals > 0:
        df["percentage"] = df.apply(lambda row: round(row["percentage"], decimals), axis=1)
    elif decimals == 0:
        df["percentage"] = df.apply(lambda row: round(row["percentage"]), axis=1)

    df = df.reset_index()
    df = df.drop(["index"], axis=1)
    return df


# ---- Lab

def df_value_counts(df, column, limit=0):
    df = df[column].value_counts().to_frame().reset_index()
    df.columns = [column, 'count']

    if limit > 0:
        df = combine_lower_n_percent_complete(df, "count", other_cols=[column], sum_columns=[], threshold=limit,
                                              decimals=1)
    return df
