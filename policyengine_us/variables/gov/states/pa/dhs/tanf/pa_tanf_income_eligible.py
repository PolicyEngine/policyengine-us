from policyengine_us.model_api import *


class pa_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF meets income eligibility requirements"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 183 - Income provisions"
    documentation = "The budget group is considered needy when countable income is less than the Family Size Allowance plus any special needs allowances. If countable income equals or exceeds FSA plus special needs, the budget group is ineligible. https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("pa_tanf_countable_income", period)
        fsa = spm_unit("pa_tanf_family_size_allowance", period)

        # Family is "needy" when countable income < FSA
        # (For initial implementation, special needs allowances not included)
        return countable_income < fsa
