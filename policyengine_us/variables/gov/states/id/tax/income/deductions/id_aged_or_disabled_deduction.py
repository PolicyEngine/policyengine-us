from policyengine_us.model_api import *


class id_aged_or_disabled_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho aged or disabled deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        disabled = person("is_disabled", period)
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.aged_or_disabled
        age_eligible = (age >= p.age_eligibility) & ~(head | spouse)
        eligible = age_eligible | disabled
        total_eligible = tax_unit.sum(eligible)
        capped_eligible = min_(total_eligible, p.max_deductions)
        return capped_eligible * p.amount
