from policyengine_us.model_api import *


class is_qmb_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for QMB (Qualified Medicare Beneficiary)"
    definition_period = MONTH
    documentation = (
        "QMB covers Part A premiums, Part B premiums, deductibles, "
        "coinsurance, and copayments. Income must be at or below 100% FPL."
    )
    reference = "https://www.cms.gov/medicare/costs/medicare-savings-programs"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.msp.eligibility.income
        fpg = person.spm_unit("spm_unit_fpg", period.this_year)
        monthly_fpg = fpg / MONTHS_IN_YEAR
        income_limit = monthly_fpg * p.qmb.fpl_limit
        countable_income = person("msp_countable_income", period)
        income_eligible = countable_income <= income_limit
        asset_eligible = person("msp_asset_eligible", period)
        is_medicare = person("is_medicare_eligible", period.this_year)
        return is_medicare & income_eligible & asset_eligible
