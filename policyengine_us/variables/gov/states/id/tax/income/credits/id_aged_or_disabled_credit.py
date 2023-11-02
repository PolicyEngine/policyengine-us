from policyengine_us.model_api import *


class id_aged_or_disabled_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho aged or disabled credit"
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
        ).gov.states.id.tax.income.credits.aged_or_disabled
        age_eligible = (age >= p.age_eligibility) & ~(head | spouse)
        eligible = age_eligible | disabled
        total_eligible = sum(eligible)
        capped_eligible = min_(total_eligible, p.max_amount)
        # The aged or disabled credit can only be claimed if the aged
        # or disabled deduction is not claimed
        aged_deduction = tax_unit("id_aged_or_disabled_deduction", period)
        credit_amount = capped_eligible * p.amount
        return where(aged_deduction == 0, credit_amount, 0)
