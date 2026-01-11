from policyengine_us.model_api import *


class nm_works_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico Works childcare deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        # Per 8.102.520.12(D) NMAC, child care deduction varies by age:
        # Under age 2: up to $200
        # Age 2 or older: up to $175
        p = parameters(
            period
        ).gov.states.nm.hca.nm_works.income.deductions.childcare

        person = spm_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period.this_year)
        childcare_expenses = spm_unit("childcare_expenses", period)

        # Max deduction per child based on age
        childcare_max_per_child = p.amount.calc(age) * is_dependent
        total_childcare_max = spm_unit.sum(childcare_max_per_child)

        return min_(childcare_expenses, total_childcare_max)
