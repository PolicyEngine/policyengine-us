from policyengine_us.model_api import *


class ma_part_b_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part B gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # M.G.L. c. 62 § 2(b)(2): Part B gross income is Massachusetts gross
        # income not included in Part A or Part C gross income.
        ma_gross_income = tax_unit("ma_gross_income", period)
        # ma_gross_income starts from irs_gross_income, which adds each
        # filer's dividends and net capital gain floored at zero. Remove those
        # same amounts: they go on Schedules B and D, and capital losses never
        # reduce Part B income (§ 2(d)(1)(M) disallows IRC § 62(a)(3)).
        # Subtracting Part A and Part C gross income instead would leave the
        # difference between their loss netting and irs_gross_income's in Part B.
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        dividends = max_(0, person("dividend_income", period))
        capital_gains = max_(0, person("capital_gains", period))
        part_a_and_c_income = tax_unit.sum(
            where(is_dependent, 0, dividends + capital_gains)
        )
        return max_(0, ma_gross_income - part_a_and_c_income)
