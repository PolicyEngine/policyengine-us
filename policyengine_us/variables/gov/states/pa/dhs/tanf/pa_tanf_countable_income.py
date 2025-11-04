from policyengine_us.model_api import *


class pa_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF total countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 183 - Income provisions"
    documentation = "Total countable income for the TANF budget group, combining countable earned and unearned income from all budget group members. This is compared to the Family Size Allowance to determine eligibility and benefit amount. https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Sum countable earned and unearned income for all budget group members
        countable_earned = person("pa_tanf_countable_earned_income", period)
        countable_unearned = person(
            "pa_tanf_countable_unearned_income", period
        )

        total_countable_per_person = countable_earned + countable_unearned

        # Sum across all members of the SPM unit (budget group)
        return spm_unit.sum(total_countable_per_person)
