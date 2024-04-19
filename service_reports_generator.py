#!/usr/bin/env python3

import argparse
import locale
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

from glpdf2csv import pdf_to_csv

# style = 'ggplot'
# style = 'bmh'
# plt.style.use(style)
# # plt.rc(grid=False)
# CHARTSDIR = Path('./charts')
# CHARTSDIR.mkdir(parents=True, exist_ok=True)


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
        '--hourly-modem-cost', action='store_true',
        help="generate chart showing team's hourly modem cost",
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
        index_col=2,
        parse_dates=True,
        date_format='%m/%d/%Y',
        decimal=',',
    )
    return df


def gen_raw_modem_df():
    # Get data from reports CSV files.
    reports = DATADIR.glob('* CAR Bangui Internet: Communications.csv')
    locale.setlocale(locale.LC_ALL, 'en_US')
    df = pd.concat([
        pd.read_csv(
            f,
            header=None,
            index_col=0,
            parse_dates=True,
            date_format="%d-%b-%y",
            thousands=','
        ) for f in reports
    ])
    df.drop_duplicates(inplace=True)
    df.sort_index(inplace=True)

    # Save combined file for verification.
    combined_file = DATADIR / "CAR Bangui Internet: Communications, combined.csv"  # noqa: E501
    df.to_csv(combined_file, header=False)

    return df


def gen_session_df(df=None, period='monthly'):
    """Includes 3 columns: Work date, Duration, Session format"""

    cols = df.columns.values
    # Remove 'Session format' column.
    df = df[[cols[0]]]
    # Convert 'Work hours' column to float.
    df = df.astype({cols[0]: 'float'})

    if period == 'monthly':
        # Resample daily data into monthly data.
        df = df.resample('M').sum()

    elif period == 'yearly':
        # Resample daily data into monthly data.
        df = df.resample('Y').sum()

    # Remove wrongly-named (after resample) index header.
    df.index.names = [0]
    return df


def gen_remote_hours_df(df):
    # Assumes input is sessions_df.
    cols = df.columns.values
    if 'Session format' not in cols:
        print("Error: No \"Session format\" column.")
        exit(1)
    idx = list(cols).index('Session format')
    return df[df[cols[idx]].str.startswith('Remote')]


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
    return df


def gen_clean_modem_expense_df():
    raw_modem_df = gen_raw_modem_df()
    # Deduplicate (each month's file includes earlier months from same qtr.).
    dfm = raw_modem_df.drop_duplicates()
    cols = dfm.columns.values
    # Remove irrelevant entries from column index 1.
    dfm = dfm[~dfm[cols[0]].str.contains(r'flybox', case=False)]
    dfm = dfm[~dfm[cols[0]].str.contains(r'bloosat', case=False)]
    excl = (
        "Telecel credit for Internet Nate Marti",  # Telecel Flybox trial
        "100 GB Telecel Internet credit via Nate",  # Telecel Flybox, 1st pmt.
    )
    dfm = dfm[~dfm[cols[0]].str.startswith(excl)]
    # Remove irrelevant entries from column index 2.
    excl = (
        'CAR ITR USD',
        'Ecobank',
        'ParCS',
    )
    dfm = dfm[~dfm[cols[1]].str.startswith(excl)]
    return dfm


def gen_comparison_df():
    dfm = gen_clean_modem_expense_df()
    # Only keep column index 4.
    dfm = dfm[[4]]
    # Rename column.
    dfm.columns = ["Modem credit"]
    # Convert to monthly data.
    dfm = dfm.resample('M').sum()

    raw_session_df = gen_raw_session_df()
    cols = raw_session_df.columns.values
    consultant_hours_df = raw_session_df[[cols[5], cols[6]]]
    cols = consultant_hours_df.columns.values
    # Remove rows with Null (NaN) values in 'Session format' column.
    dfs = consultant_hours_df.loc[consultant_hours_df[cols[1]].notna(), :]  # noqa: E501
    # Keep only Remote sessions.
    dfs = gen_remote_hours_df(dfs)
    # Rename long-named columns.
    dfs = dfs.rename(columns={cols[0]: "Session hours"})
    dfs = gen_session_df(dfs, period='monthly')

    df = dfs.join(dfm)
    cols = df.columns.values
    # Change 'NaN' values in 'Modem credit' column to '0'.
    df[cols[1]] = df[cols[1]].fillna(0)
    print("gen_comparison_df:")
    df["FCFA/hr"] = df.apply(calculate_monthly_rate, axis=1)
    df["Cum. Hrs."] = df[cols[0]].cumsum()
    df["Cum. Credit"] = df[cols[1]].cumsum()
    df["FCFA/hr-to-date"] = df.apply(calculate_cum_rate, axis=1)
    print(df.to_string())
    return df


def gen_comparison_plot(title=None):
    # Get DataFrame.
    df = gen_comparison_df()
    cols = df.columns.values
    # Remove 'NaN' values.
    df = df.loc[df[cols[1]].notna(), :]

    rot = 45
    width = 0.5

    fig, ax = plt.subplots(1)
    ax1 = df[cols[5]].plot(
        ax=ax,
        secondary_y=cols[5],
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
    # ax.legend(loc=0)
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper left')
    plt.title(title)
    return df


def gen_modem_cost_per_team_df():
    dfm = gen_clean_modem_expense_df()
    dft = gen_teams_df()
    teams = dft.columns.values
    totals = {}
    for team in teams:
        totals[team] = [0, 0]
    # Add total modem cost to data dict.
    for _, row in dfm.iterrows():
        for team in teams:
            if team.lower() in row[1] or team in row[1]:
                totals[team][0] += row[4]
    # Add total checking hours to data dict.
    cols = dft.columns.values
    for _, row in dft.iterrows():
        for i, col in enumerate(cols):
            totals[col][1] += row[i]
    # Build dataframe.
    df = pd.Series({k: v[0] / v[1] for k, v in totals.items()})
    return df


def gen_modem_cost_per_team_plot(title=None):
    df = gen_modem_cost_per_team_df()
    df.plot(
        kind='bar',
        figsize=(16, 9),
        ylabel="FCFA/hr",
        rot=45,
    )
    plt.title(title)
    return df


def gen_teams_df():
    """Take data from raw sessions and create new table."""
    df = gen_raw_session_df()
    cols = df.columns.values
    # Remove 'None' rows from column index 5 (Hours).
    df = df.loc[df[cols[5]].notna(), :]
    # Remove 'None' rows from column index 6 (Session format).
    df = df.loc[df[cols[6]].notna(), :]
    # Keep only 'Remote session' rows.
    df = df[df[cols[6]].str.startswith('Remote')]
    # Remove hours not attributed to team budgets.
    excl = (
        "IT and Language Technology services, ACATBA",
    )
    df = df[~df[cols[2]].str.startswith(excl)]
    # Keep only Team name and session hours columns.
    df = df[[cols[2], cols[5]]]
    cols = df.columns.values
    # Split each team into own column.
    teams = list(set(df[cols[0]].values))
    teams.sort()
    # new_cols = ['Work date', *teams]
    new_df = pd.DataFrame(columns=teams)
    for index, row in df.iterrows():
        team = row[0]
        hours = float(row[1])
        if index in new_df.index.values:
            # Update the row with additional data.
            new_df.at[index, team] = hours
        else:
            # Add new row at given index.
            team_index = teams.index(team)
            new_row = [0 for i in range(len(teams))]  # initialize with zeros
            new_row[team_index] = hours  # add hours to row
            new_df.loc[index] = new_row  # put row at end of df
            new_df = new_df.sort_index()  # sort df
    return new_df


def gen_teams_plot(title=None):
    df = gen_teams_df()
    # Resample on months.
    df = df.resample('M').sum()

    # Prepare plot.
    ax = df.plot(
        kind='bar',
        figsize=(16, 9),
        ylabel="Hours",
        rot=45,
        width=1,
    )
    ax.set_xticklabels(map(monthly_fmt, df.index))
    ax.set_xlabel(None)
    plt.title(title)
    return df


def calculate_monthly_rate(row):
    if not row[1].is_integer():
        # print(row[1])
        rate = None
    elif row[0] == 0:
        rate = float(0)
    else:
        rate = round(row[1] / row[0])
    return rate


def calculate_cum_rate(row):
    if not row[4].is_integer():
        # print(row[1])
        rate = None
    elif row[3] == 0:
        rate = float(0)
    else:
        rate = round(row[4] / row[3])
    return rate


def publish_plot(df=None, outfile=None, title=None):
    if outfile is None:
        outfile = CHARTSDIR / f"{title}.png"
        csvfile = DATADIR / f"{title}.csv"

    if not outfile:
        plt.show()
    else:
        plt.savefig(outfile)
        df.to_csv(csvfile)


def make_local_chart(outfile, df, period):
    title = "SIL CAR Face-to-Face Session Hours"
    cols = df.columns.values
    if 'Session format' not in cols:
        print("Error: No \"Session format\" column.")
        exit()
    idx = list(cols).index("Session format")
    local_hours_df = df[df[cols[idx]].str.startswith('In person')]
    df_to_plot = gen_session_df(df=local_hours_df, period=period)
    df = gen_session_plot(df_to_plot, title, period)
    publish_plot(df, outfile, title)


def make_modem_rate_chart(outfile):
    title = "SIL CAR Modem Cost per Remote Session Hour"
    df = gen_comparison_plot(title)
    publish_plot(df, outfile, title)


def make_remote_chart(outfile, df, period):
    title = "SIL CAR Remote Session Hours"
    cols = df.columns.values
    if 'Session format' not in cols:
        print("Error: No \"Session format\" column.")
        exit()
    idx = list(cols).index("Session format")
    # Only keep rows where 'Session format' starts with 'Remote'.
    remote_hours_df = df[df[cols[idx]].str.startswith('Remote')]
    df_to_plot = gen_session_df(df=remote_hours_df, period=period)
    df = gen_session_plot(df_to_plot, title, period)
    publish_plot(df, outfile, title)


def make_teams_chart(outfile):
    title = "ACATBA Teams' Remote Session Hours"
    df = gen_teams_plot(title)
    publish_plot(df, outfile, title)


def make_hourly_modem_cost_chart(outfile):
    title = "Modem Credit per Remote Session Hour"
    df = gen_modem_cost_per_team_plot(title)
    publish_plot(df, outfile, title)


def test():
    """ For testing new features. """
    gen_modem_cost_per_team_df()
    exit()
    pass


def main():
    # pd.set_option('copy_on_write', True)
    args = parse_cli()

    style = 'bmh'
    plt.style.use(style)
    plt.rc('axes', axisbelow=True)

    global COLORS
    COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']

    global CHARTSDIR
    CHARTSDIR = Path(__file__).parent / 'charts'
    CHARTSDIR.mkdir(parents=True, exist_ok=True)

    drive_dir = Path.home() / 'Drive'
    global REPORTSDIR
    rep_dirs = [d for d in drive_dir.rglob('GL Reports')]
    REPORTSDIR = rep_dirs[0] if rep_dirs else None
    if not REPORTSDIR:
        print("Error: \"GL Reports\" folder not found.")
        exit(1)

    global DATADIR
    DATADIR = REPORTSDIR.parent / 'GL Data'
    DATADIR.mkdir(parents=True, exist_ok=True)

    # Convert GL PDF reports to CSV.
    for r in REPORTSDIR.glob('* Bangui Internet-donor*.pdf'):
        pdf_to_csv(r, outdir=DATADIR)
    print()

    if args.test:
        test()
        exit()

    raw_df = gen_raw_session_df()
    cols = raw_df.columns.values
    consultant_hours_df = raw_df[[cols[5], cols[6]]]
    cols = consultant_hours_df.columns.values
    # Remove rows with Null (NaN) values in 'Session format' column.
    sessions_df = consultant_hours_df.loc[consultant_hours_df[cols[1]].notna(), :]  # noqa: E501

    outfile = None
    if args.show:
        outfile = False

    period = 'monthly'
    if args.yearly:
        period = 'yearly'

    if args.remote:
        make_remote_chart(outfile, sessions_df, period)

    if args.hourly_modem_cost:
        make_hourly_modem_cost_chart(outfile)

    if args.local:
        make_local_chart(outfile, sessions_df, period)

    if args.modem_rate:
        make_modem_rate_chart(outfile)

    if args.teams:
        make_teams_chart(outfile)

    if args.all:
        make_hourly_modem_cost_chart(outfile)
        make_local_chart(outfile, sessions_df, period)
        make_modem_rate_chart(outfile)
        make_remote_chart(outfile, sessions_df, period)
        make_teams_chart(outfile)


if __name__ == '__main__':
    main()
