from policyengine_us.model_api import *


class in_ccdf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Indiana CCDF countable income"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=26"
    )

    def formula(spm_unit, period, parameters):
        gross_income = spm_unit("in_ccdf_gross_income", period)
        # We don't track foster-family income, documented-CPS-family income,
        # or lump-sum Social Security and earned-income payroll adjustments
        # (advance pay timing, insurance, reimbursements, housing/food
        # allowances, employer retirement contributions) at the moment, so
        # those exclusions are not separately modeled (PM Section 1.8
        # #page=26, #page=27, #page=29).
        # Earned income of household members under 18 is excluded, except for
        # emancipated minors and minor parents, which we don't track at the
        # moment.
        person = spm_unit.members
        is_minor = person("age", period.this_year) < 18
        minor_earned_income = spm_unit.sum(
            is_minor
            * add(person, period, ["employment_income", "self_employment_income"])
        )
        return gross_income - minor_earned_income
