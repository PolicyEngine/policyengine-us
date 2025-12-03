from policyengine_us.model_api import *


class is_slmb_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for SLMB (Specified Low-Income Medicare Beneficiary)"
    definition_period = MONTH
    documentation = (
        "SLMB covers Part B premiums only. "
        "Income must be between 100% and 120% FPL."
    )
    reference = "https://www.cms.gov/medicare/costs/medicare-savings-programs"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.msp.eligibility.income
        fpg = person.spm_unit("spm_unit_fpg", period.this_year)
        monthly_fpg = fpg / MONTHS_IN_YEAR
        countable_income = person("msp_countable_income", period)
        # Must be above QMB threshold and at or below SLMB threshold
        qmb_limit = monthly_fpg * p.qmb.fpl_limit
        slmb_limit = monthly_fpg * p.slmb.fpl_limit
        income_eligible = (countable_income > qmb_limit) & (
            countable_income <= slmb_limit
        )
        asset_eligible = person("msp_asset_eligible", period)
        is_medicare = person("is_medicare_eligible", period.this_year)
        return is_medicare & income_eligible & asset_eligible
