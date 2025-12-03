from policyengine_us.model_api import *


class is_qi_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Qualifying Individual (QI) eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.123",
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
    )

    def formula(person, period, parameters):
        # QI requires income above 120% FPL but at or below 135% FPL
        p = parameters(period).gov.hhs.medicare.savings_programs.eligibility

        medicare_eligible = person("is_medicare_eligible", period.this_year)
        asset_eligible = person("msp_asset_eligible", period)

        fpg = person.spm_unit("spm_unit_fpg", period.this_year)
        monthly_fpg = fpg / MONTHS_IN_YEAR
        countable_income = person("msp_countable_income", period)

        slmb_income_limit = monthly_fpg * p.income.slmb.fpl_limit
        qi_income_limit = monthly_fpg * p.income.qi.fpl_limit

        income_above_slmb = countable_income > slmb_income_limit
        income_at_or_below_qi = countable_income <= qi_income_limit
        income_eligible = income_above_slmb & income_at_or_below_qi

        return medicare_eligible & income_eligible & asset_eligible
