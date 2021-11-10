import calendar


class Utils:
    @staticmethod
    def get_yy_mm_str1(a_date):
        month_yy = calendar.monthrange(a_date.year, a_date.month)
        return [str(a_date.year) + '-' + str(a_date.month).rjust(2, '0'), month_yy]

    @staticmethod
    def get_yy_mm_str(year, month):
        return str(year) + '-' + str(month).rjust(2, '0')

