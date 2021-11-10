import calendar
import warnings
from datetime import datetime
from collections import OrderedDict

from Utils import Utils


class Employer:
    def __init__(self, emp_no):
        self.emp_no = emp_no
        self.__active_buckets = []
        self.__monthly_buckets = dict()
        self.total_amount = 0
        self.tiers = set()
        self.added_on = None

    def is_new(self):
        return len(self.__active_buckets) == 1

    def get_active_buckets(self):
        self.__active_buckets.sort(key=lambda x: x.effective_to)
        return self.__active_buckets

    def get_monthly_buckets(self):
        return OrderedDict(sorted(self.__monthly_buckets.items()))

    def add_to_bucket(self, effective_from, effective_to, status, tier, added_on):
        from_date = datetime.strptime(effective_from, "%Y-%m-%d").date()
        to_date = datetime.strptime(effective_to, "%Y-%m-%d").date()
        self.tiers.add(tier)
        if added_on:
            self.added_on = Utils.get_yy_mm_str1(from_date)[0]

        # Adding to Active buckets
        bucket = self.ActiveBucket(from_date, to_date, status, tier)
        self.__active_buckets.append(bucket)

    def add_amount(self, amount_date, cash):
        a_date = datetime.strptime(amount_date, "%d/%m/%Y").date()
        bucket = self.get_bucket(a_date)
        if bucket:
            bucket.add_amount(cash)
            self.total_amount += float(cash)

            # Adding to month bucket
            [monthYYStr, monthYY] = Utils.get_yy_mm_str1(a_date)
            if monthYYStr not in self.__monthly_buckets:
                m_bucket = self.MonthlyBucket(monthYY[1], a_date.month, a_date.year, bucket.tier, bucket.status)
            else:
                m_bucket = self.__monthly_buckets[monthYYStr]
                m_bucket.is_new = False
            m_bucket.add_amount(cash)
            self.__monthly_buckets[monthYYStr] = m_bucket
        else:
            warnings.warn('Warning: employer (' + self.emp_no + ') was not active for: ' + amount_date)

    def get_bucket(self, bucket_date):
        for bucket in self.__active_buckets:
            if bucket.effective_from <= bucket_date <= bucket.effective_to:
                return bucket
        return None

    def get_records(self, month, year):
        month = calendar.monthrange(year, month)
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, month[1]).date()

        for b in self.__active_buckets:
            if b.effective_from <= start_date and end_date <= b.effective_to:
                return b

    class MonthlyBucket:
        def __init__(self, day, month, year, tier, status):
            self.__end_date = datetime(year, month, day)
            self.__start_date = datetime(year, month, 1)
            self.tier = tier
            self.status = status
            self.amount = 0
            self.count = 0
            self.is_new = True

        def add_amount(self, amount):
            self.amount += float(amount)
            self.count += 1

    class ActiveBucket:
        def __init__(self, effective_from, effective_to, status, tier):
            self.effective_from = effective_from
            self.effective_to = effective_to
            self.tier = tier
            self.status = status
            self.amount = 0
            self.count = 0

        def add_amount(self, amount):
            self.amount += float(amount)
            self.count += 1
