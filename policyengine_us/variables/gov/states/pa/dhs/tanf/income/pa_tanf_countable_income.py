from policyengine_us.model_api import *


class pa_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Aggregate person-level countable earned income
        countable_earned = spm_unit.sum(
            person("pa_tanf_earned_income_after_deductions_person", period)
        )

        # All unearned income is countable (no deductions)
        countable_unearned = spm_unit.sum(
            person("tanf_gross_unearned_income", period)
        )

        # Total countable income
        return countable_earned + countable_unearned
