from policyengine_us.model_api import *


class msp_income_eligible(Variable):
    value_type = bool
    entity = Person
    unit = USD
    label = "Medicare Savings Program income eligible"
    definition_period = MONTH
    documentation = "Eligible for any MSP level based on income (QI threshold of 135% FPL)."
    reference = "https://www.cms.gov/medicare/costs/medicare-savings-programs"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.msp.eligibility.income
        # Use the highest threshold (QI at 135% FPL) to determine
        # if person is income-eligible for any MSP level
        qi_fpl_limit = p.qi.fpl_limit
        fpg = person.spm_unit("spm_unit_fpg", period.this_year)
        monthly_fpg = fpg / MONTHS_IN_YEAR
        income_limit = monthly_fpg * qi_fpl_limit
        countable_income = person("msp_countable_income", period)
        return countable_income <= income_limit
