#!/usr/bin/env python3

""" Convert GL report from PDF to CSV for given account.
    (default: "Bangui Internet: Communications")
"""

import csv
import pdftotext
import re
import sys

from pathlib import Path


def get_date_from_file_name(pdf_file_path_obj):
    file_name = pdf_file_path_obj.name
    m = re.match(r'^\d{4}', file_name)
    if m:
        date = m[0]
    else:
        print("Error: Filename doesn't start with 4 digits.")
        exit(1)
    return date


def text_from_pdf(pdf_file_path_obj):
    print(f"Reading: {pdf_file_path_obj.name}")
    with pdf_file_path_obj.open('rb') as f:
        pdf_pgs = pdftotext.PDF(f)

    plain_text = '\n'.join(pdf_pgs)
    return plain_text


def filter_account_entries(report_text, full_account_name):
    expr = rf'^ *\d{{5}}-R51057 +{full_account_name}\s+Beginning Balance.*\n((?: *GLJE.+\n)+)'  # noqa: E501
    account_text_results_pgs = re.findall(expr, report_text, flags=re.MULTILINE)  # noqa: E501
    account_entry_lines = []
    if len(account_text_results_pgs) == 0:
        print(f"No data found for: {full_account_name}")
        return account_entry_lines

    for pg in account_text_results_pgs:
        account_entry_lines.extend(pg.split('\n'))
    # Remove empty lines.
    account_entry_lines = [ln for ln in account_entry_lines if len(ln) > 0]
    # account_entry_lines = account_text_results[0].split('\n')
    return account_entry_lines


def write_lines_to_csv(lines, csv_file_path_obj):
    # Strip 1st 3 columns.
    stripped_lines = []
    expr = r' *GLJE +[0-9]{6} +[0-9]{2} +'
    for line in lines:
        stripped_lines.append(re.sub(expr, '', line))
    # Convert multiple spaces to tabs.
    tabbed_lines = []
    col_sep_expr = r' {2,}'
    for line in stripped_lines:
        tabbed_lines.append(re.sub(col_sep_expr, '\t', line))
    # # Only keep last 6 columns.
    # filtered_tabbed_lines = []
    # for line in tabbed_lines:
    #     print(line)
    #     columns = line.split('\t')
    #     filtered_tabbed_lines.append('\t'.join(columns[-6:]))
    # Write to CSV.
    # global csv
    csv_rows = csv.reader(tabbed_lines, delimiter='\t')
    with csv_file_path_obj.open('w') as f:
        csvw = csv.writer(f)
        csvw.writerows(csv_rows)


def pdf_to_csv(pdf_file, account_name=None, outdir=None):
    pdfobj = Path(pdf_file)
    date = get_date_from_file_name(pdfobj)
    if not account_name:
        account_name = "Bangui Internet: Communications"

    csv_filename = f"{date} CAR {account_name}.csv"
    if not outdir:
        csv_parent = pdfobj.parent
    else:
        csv_parent = Path(outdir)
    csv_file = csv_parent / csv_filename
    text = text_from_pdf(pdfobj)
    account_entry_lines = filter_account_entries(text, account_name)
    if account_entry_lines:
        write_lines_to_csv(account_entry_lines, csv_file)


def main():
    if sys.argv[1] in ['-h', '--help']:
        print(f"usage: {sys.argv[0]} /PATH/TO/PDF")
        exit()
    pdf_file = Path(sys.argv[1]).expanduser().resolve()
    account_name = None
    if len(sys.argv) > 2:
        account_name = sys.argv[2]
    pdf_to_csv(pdf_file, account_name=account_name)


if __name__ == '__main__':
    main()
