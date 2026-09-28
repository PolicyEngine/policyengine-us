from policyengine_us.model_api import *


class ks_liheap_countable_interest_dividend_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Kansas LIEAP countable interest and dividend income"
    documentation = "Recurring interest and dividends, excluding interest of children under 18 and the FY2025 monthly exemption. Set countable income directly for exempt burial-fund interest or FY2026 irregular, unpredictable payments below the quarterly exemption."
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13360.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13360.htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.income
        age = spm_unit.members("age", period)
        interest = spm_unit.members("interest_income", period)
        adult_interest = spm_unit.sum(
            where(age >= p.interest_income_min_age, interest, 0)
        )
        dividends = add(spm_unit, period, ["dividend_income"])
        total = adult_interest + dividends
        threshold = p.regular_interest_dividend_exemption * MONTHS_IN_YEAR
        return where(total > threshold, total, 0)
