import calendar
import csv
import warnings
from datetime import datetime

from Employer import Employer
from Utils import Utils


def read_input_csv():
    employers = dict()
    with open('Employer master.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                if row[0] not in employers:
                    emp = Employer(row[0])
                    added_on = True
                else:
                    emp = employers[row[0]]
                    added_on = False
                emp.add_to_bucket(row[1], row[2], row[3], row[4], added_on)
                employers[row[0]] = emp
            line_count += 1

    with open('Payment transactions.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                if row[0] not in employers:
                    warnings.warn('Warning: employer Record not found: ' + row[0])
                else:
                    emp = employers[row[0]]
                    emp.add_amount(row[1], row[2])
            line_count += 1
    return employers


def generate_table(employers, year):
    start = datetime.strptime(str(year) + '-01-01', "%Y-%m-%d").date()
    end = datetime.strptime(str(year) + '-12-31', "%Y-%m-%d").date()
    emps = []
    tiers = set()

    for (key, value) in employers.items():
        for bucket in value.get_active_buckets():
            if bucket.effective_from <= start and bucket.effective_to <= end:
                if emps.count(value) == 0:
                    emps.append(value)
                    tiers = tiers.union(value.tiers)

    rows = list()
    for tier in tiers:
        for i in range(1, 13):
            month = calendar.monthrange(year, i)
            row = dict()
            rows.append(row)
            amount = 0
            payments = 0
            open_status = 0
            new_addition = 0

            mm_yy_str = Utils.get_yy_mm_str(year, i)
            for emp in emps:
                m_buckets = emp.get_monthly_buckets()
                if mm_yy_str in m_buckets:
                    m_bucket = m_buckets[mm_yy_str]
                    amount += m_bucket.amount
                    payments += m_bucket.count
                    if m_bucket.status == 'Open':
                        open_status += 1
                    if mm_yy_str.find(emp.added_on) > 0:
                        new_addition += 1

            row['Tier'] = tier
            row['Month end date'] = datetime(year, i, month[1]).date().strftime('%d/%m/%Y')
            row['Num payments'] = payments
            row['Amount of payments'] = amount
            row['New employers'] = new_addition
            row['Open employers at EOM'] = open_status
    return rows


if __name__ == '__main__':
    emps = read_input_csv()
    results = generate_table(emps, 2018)
    results = sorted(results, key=lambda x: (x['Tier'], x['Month end date']))
    keys = results[0].keys()
    with open('people.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)
    print("Table Generated")
