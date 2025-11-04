from policyengine_us.model_api import *


class pa_tanf_benefit_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF benefit amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 183 - Benefit calculation"
    documentation = "Monthly Pennsylvania TANF cash assistance benefit, calculated as Family Size Allowance plus special needs allowances minus total countable income. Payment is issued in two increments per month. https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    def formula(spm_unit, period, parameters):
        # Benefit = FSA + special needs allowances - countable income
        fsa = spm_unit("pa_tanf_family_size_allowance", period)
        countable_income = spm_unit("pa_tanf_countable_income", period)

        # For initial implementation, special needs allowances not included
        # Calculate benefit (cannot be negative)
        benefit = max_(fsa - countable_income, 0)

        # Only eligible households receive benefits
        eligible = spm_unit("pa_tanf_eligible", period)

        return where(eligible, benefit, 0)
