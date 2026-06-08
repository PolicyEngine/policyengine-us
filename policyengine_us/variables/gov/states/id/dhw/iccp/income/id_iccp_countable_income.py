from policyengine_us.model_api import *


class id_iccp_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Idaho Child Care Program countable income"
    defined_for = StateCode.ID
    reference = (
        "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=7",
        "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=8",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.dhw.iccp
        person = spm_unit.members
        age = person("age", period.this_year)
        is_parent = person("is_tax_unit_head_or_spouse", period.this_year)
        child_earnings_counted = (
            age >= p.income.child_earnings_age_threshold
        ) | is_parent
        earned_per_person = add(person, period, p.income.earned_sources)
        earned_income = spm_unit.sum(earned_per_person * child_earnings_counted)
        unearned_income = add(spm_unit, period, p.income.unearned_sources)
        deductions = add(spm_unit, period, p.income.deductions)
        return max_(earned_income + unearned_income - deductions, 0)
