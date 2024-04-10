#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# style = 'ggplot'
# style = 'bmh'
# plt.style.use(style)
# # plt.rc(grid=False)
# OUTDIR = Path('./charts')
# OUTDIR.mkdir(parents=True, exist_ok=True)


def parse_cli():
    parser = argparse.ArgumentParser(
        prog="ServiceReportsGenerator",
        description="Generate reports from SIL CAR Services data",
    )
    parser.add_argument(
        '--all', action='store_true',
        help="produce all configured charts",
    )
    parser.add_argument(
        '--local', action='store_true',
        help="only include data from local 'face-to-face' sessions",
    )
    parser.add_argument(
        '--modem-rate', action='store_true',
        help="generate chart showing modem cost per session hour",
    )
    parser.add_argument(
        '--remote', action='store_true',
        help="only include data from remote sessions",
    )
    parser.add_argument(
        '--teams', action='store_true',
        help="generate chart show teams' monthly session hours",
    )
    parser.add_argument(
        '--yearly', '-y', action='store_true',
        help="use yearly data instead of monthly",
    )
    parser.add_argument(
        '--show', '-s', action='store_true',
        help="show chart in new window rather than save to file",
    )
    parser.add_argument(
        '--test', action='store_true',
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def daily_fmt(label):
    return label.date()


def monthly_fmt(label):
    return f"{label.month_name()}\n{label.year}"


def yearly_fmt(label):
    return label.year


def gen_raw_session_df():
    csv_name = "SIL CAR services reporting (Responses) - Form Responses 2.csv"
    responses_file = Path.home() / "Téléchargements" / csv_name

    df = pd.read_csv(
        responses_file,
        parse_dates=True,
        date_format='%m/%d/%Y',
        decimal=',',
    )
    return df


def gen_raw_modem_df():
    reports_dir = Path.home() / Path("Drive/SIL Documents/Information (IT) Systems/internet purchases/GL Reports")  # noqa: E501
    reports_file = reports_dir / "Combined CAR Bangui Internet.csv"
    df = pd.read_csv(
        reports_file,
        header=None,
        index_col=0,
        parse_dates=True,
        date_format="%d/%m/%Y",
        thousands=','
    )
    return df


def gen_session_df(df=None, period='monthly'):
    """Includes 3 columns: Work date, Duration, Session format"""

    cols = list(df.columns.values)
    # Remove 'Session format' column.
    df = df[[cols[0], cols[1]]]
    # Convert 'Work hours' column to float.
    df = df.astype({cols[1]: 'float'})
    # Convert labels to dateformat.
    df[cols[0]] = pd.to_datetime(df[cols[0]])

    if period == 'monthly':
        # Resample daily data into monthly data.
        df = df.resample('M', on=cols[0]).sum()

    elif period == 'yearly':
        # Resample daily data into monthly data.
        df = df.resample('Y', on=cols[0]).sum()

    # Remove index header.
    df.index.names = [0]
    return df


def gen_remote_hours_df(df):
    # Assumes input is sessions_df.
    cols = list(df.columns.values)
    return df[df[cols[2]].str.startswith('Remote')]


def gen_session_plot(df=None, title=None, period='monthly'):
    """Includes 3 columns: Work date, Duration, Session format"""

    if period == 'monthly':
        # Format the x-axis.
        ax = df.plot(figsize=(16, 9), kind='bar', rot=45)
        ax.set_xticklabels(map(monthly_fmt, df.index))

    elif period == 'yearly':
        # Format the x-axis.
        ax = df.plot(figsize=(16, 9), kind='bar', rot=45)
        ax.set_xticklabels(map(yearly_fmt, df.index))

    # Format the plot.
    ax.get_legend().remove()
    ax.set_ylabel("Hours")
    ax.set_xlabel(None)
    plt.title(title)
    plt.rcParams.update({'font.size': 10})


def gen_comparison_df():
    raw_modem_df = gen_raw_modem_df()
    # Deduplicate (each month's file includes earlier months from same qtr.).
    dfm = raw_modem_df.drop_duplicates()
    # Remove irrelevant entries from column index 1.
    dfm = dfm[~dfm[1].str.contains(r'flybox', case=False)]
    dfm = dfm[~dfm[1].str.contains(r'bloosat', case=False)]
    # Remove irrelevant entries from column index 2.
    excl = (
        'CAR ITR USD',
        'Ecobank',
        'ParCS',
    )
    dfm = dfm[~dfm[2].str.startswith(excl)]
    # Convert dates to DateTimes.
    dfm.index = pd.to_datetime(dfm.index, format="%d-%b-%y")
    # Only keep column index 4.
    dfm = dfm[[4]]
    # Rename column.
    dfm.columns = ["Modem credit"]
    # Convert to monthly data.
    dfm = dfm.resample('M').sum()

    raw_session_df = gen_raw_session_df()
    cols = list(raw_session_df.columns.values)
    consultant_hours_df = raw_session_df[[cols[2], cols[6], cols[7]]]
    # Remove rows with Null (NaN) values in 'Session format' column.
    dfs = consultant_hours_df.loc[consultant_hours_df[cols[7]].notna(), :]  # noqa: E501
    # Keep only Remote sessions.
    dfs = gen_remote_hours_df(dfs)
    # Rename long-named columns.
    dfs = dfs.rename(columns={cols[6]: "Session hours"})
    dfs = gen_session_df(dfs, period='monthly')

    df = dfs.join(dfm)
    cols = list(df.columns.values)
    df["FCFA/hour"] = df.apply(calculate_rate, axis=1)
    print(df.to_string())
    return df


def gen_comparison_plot(title=None):
    # Get DataFrame.
    df = gen_comparison_df()
    cols = list(df.columns.values)
    # Remove 'NaN' values.
    df = df.loc[df[cols[1]].notna(), :]

    rot = 45
    width = 0.5

    fig, ax = plt.subplots(1)
    ax1 = df[cols[2]].plot(
        ax=ax,
        secondary_y=cols[2],
        ylabel="FCFA",
        use_index=False,
        color=COLORS[1],
        marker='o',
        lw=3,
        legend=True,
    )
    ax2 = df[cols[0]].plot(
        ax=ax,
        kind='bar',
        color=COLORS[0],
        width=width,
        rot=rot,
        legend=True,
        figsize=(16, 9),
    )
    ax.set_ylabel("Hours")
    ax1.grid(False)
    ax2.grid(False)
    ax.set_xticklabels(map(monthly_fmt, df.index))
    ax.set_xlabel(None)
    plt.title(title)


def gen_teams_df():
    """Take data from raw sessions and create new table."""
    df = gen_raw_session_df()
    cols = df.columns.values
    # Remove 'None' rows.
    df = df.loc[df[cols[7]].notna(), :]
    # Keep only 'Remote session' rows.
    df = df[df[cols[7]].str.startswith('Remote')]
    # Remove unneeded columns.
    df = df[[*cols[2:4], cols[6]]]
    cols = df.columns.values
    # Convert dates to DateFormat.
    df[cols[0]] = pd.to_datetime(df[cols[0]])
    # Split each team into own column.
    teams = list(set(df[cols[1]].values))
    teams.sort()
    new_cols = ['Work date', *teams]
    new_df = pd.DataFrame(columns=new_cols)
    for index, row in df.iterrows():
        idx = new_cols.index(row[1])
        new_row = [0 for i in range(len(new_cols))]
        new_row[0] = row[0]
        new_row[idx] = float(row[2])
        new_df.loc[-1] = new_row
        new_df.index = new_df.index + 1
        new_df = new_df.sort_index()

    # Resample on months.
    df = new_df.resample('M', on=cols[0]).sum()
    return df


def gen_teams_plot(title=None):
    df = gen_teams_df()
    ax = df.plot(
        kind='bar',
        figsize=(16, 9),
        ylabel="Hours",
        rot=45,
        width=0.75,
    )
    ax.set_xticklabels(map(monthly_fmt, df.index))
    ax.set_xlabel(None)
    plt.title(title)


def calculate_rate(row):
    if not row[1].is_integer():
        # print(row[1])
        rate = None
    elif row[0] == 0:
        rate = float(0)
    else:
        rate = round(row[1] / row[0])
    return rate


def publish_plot(outfile=None, title=None):
    if outfile is None:
        outfile = OUTDIR / f"{title}.png"

    if not outfile:
        plt.show()
    else:
        plt.savefig(outfile)


def make_local_chart(outfile, df, cols, period):
    title = "SIL CAR Face-to-Face Session Hours"
    local_hours_df = df[df[cols[7]].str.startswith('In person')]
    df_to_plot = gen_session_df(df=local_hours_df, period=period)
    gen_session_plot(df_to_plot, title, period)
    publish_plot(outfile, title)


def make_modem_rate_chart(outfile):
    title = "SIL CAR Modem Cost per Remote Session Hour"
    gen_comparison_plot(title)
    publish_plot(outfile, title)


def make_remote_chart(outfile, df, cols, period):
    title = "SIL CAR Remote Session Hours"
    # Only keep rows where 'Session format' starts with 'Remote'.
    remote_hours_df = df[df[cols[7]].str.startswith('Remote')]
    df_to_plot = gen_session_df(df=remote_hours_df, period=period)
    gen_session_plot(df_to_plot, title, period)
    publish_plot(outfile, title)


def make_teams_chart(outfile):
    title = "ACATBA Teams' Remote Session Hours"
    gen_teams_plot(title)
    publish_plot(outfile, title)


def test():
    """ For testing new features. """
    pass


def main():
    style = 'bmh'
    plt.style.use(style)
    plt.rc('axes', axisbelow=True)

    global COLORS
    COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']

    global OUTDIR
    OUTDIR = Path('./charts')
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # pd.set_option('copy_on_write', True)
    args = parse_cli()

    if args.test:
        test()
        exit()

    raw_df = gen_raw_session_df()
    cols = list(raw_df.columns.values)
    consultant_hours_df = raw_df[[cols[2], cols[6], cols[7]]]
    # Remove rows with Null (NaN) values in 'Session format' column.
    sessions_df = consultant_hours_df.loc[consultant_hours_df[cols[7]].notna(), :]  # noqa: E501

    outfile = None
    if args.show:
        outfile = False

    period = 'monthly'
    if args.yearly:
        period = 'yearly'

    if args.remote:
        make_remote_chart(outfile, sessions_df, cols, period)

    if args.local:
        make_local_chart(outfile, sessions_df, cols, period)

    if args.modem_rate:
        make_modem_rate_chart(outfile)

    if args.teams:
        make_teams_chart(outfile)

    if args.all:
        make_local_chart(outfile, sessions_df, cols, period)
        make_remote_chart(outfile, sessions_df, cols, period)
        make_modem_rate_chart(outfile)
        make_teams_chart(outfile)


if __name__ == '__main__':
    main()
