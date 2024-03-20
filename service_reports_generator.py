#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

OUTDIR = Path('./charts')
OUTDIR.mkdir(parents=True, exist_ok=True)


def parse_cli():
    parser = argparse.ArgumentParser(
        prog="ServiceReportsGenerator",
        description="Generate reports from SIL CAR Services data",
    )
    parser.add_argument(
        '--local', action='store_true',
        help="only include data from local 'face-to-face' sessions"
    )
    parser.add_argument(
        '--remote', action='store_true',
        help="only include data from remote sessions",
    )
    parser.add_argument(
        '--yearly', '-y', action='store_true',
        help="use yearly data instead of monthly"
    )
    parser.add_argument(
        '--show', '-s', action='store_true',
        help="show chart in new window rather than save to file"
    )
    return parser.parse_args()


def daily_fmt(label):
    return label.date()


def monthly_fmt(label):
    return f"{label.month_name()}\n{label.year}"


def yearly_fmt(label):
    return label.year


def gen_session_chart(df=None, title=None, outfile=None, period='monthly'):
    """Includes 3 columns: Work date, Duration, Session format"""

    if outfile is None:
        outfile = OUTDIR / f"{title}.png"

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
        # Format the x-axis.
        ax = df.plot(kind='bar', rot=45)
        ax.set_xticklabels(map(monthly_fmt, df.index))

    elif period == 'yearly':
        # Resample daily data into monthly data.
        df = df.resample('Y', on=cols[0]).sum()
        # Format the x-axis.
        ax = df.plot(kind='bar', rot=45)
        ax.set_xticklabels(map(yearly_fmt, df.index))

    # Format the plot.
    ax.get_legend().remove()
    plt.title(title)
    plt.ylabel("Hours")
    plt.rcParams.update({'font.size': 10})

    if not outfile:
        plt.show()
    else:
        plt.savefig(outfile)


def main():
    args = parse_cli()

    csv_name = "SIL CAR services reporting (Responses) - Form Responses 2.csv"
    responses_file = Path.home() / "Téléchargements" / csv_name

    raw_df = pd.read_csv(
        responses_file,
        parse_dates=True,
        date_format='%m/%d/%Y',
        decimal=',',
    )

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
        title = "SIL CAR Remote session hours"
        # Remove rows where 'Session format' doesn't start with 'Remote'.
        remote_hours_df = sessions_df[sessions_df[cols[7]].str.startswith('Remote')]  # noqa: E501
        gen_session_chart(remote_hours_df, title, outfile, period)

    elif args.local:
        title = "SIL CAR Face-to-Face session hours"
        local_hours_df = sessions_df[sessions_df[cols[7]].str.startswith('In person')]  # noqa: E501
        gen_session_chart(local_hours_df, title, outfile, period)

    elif not args.remote and not args.local:
        title = "SIL CAR Total session hours"
        gen_session_chart(sessions_df, title, outfile, period)


if __name__ == '__main__':
    main()
