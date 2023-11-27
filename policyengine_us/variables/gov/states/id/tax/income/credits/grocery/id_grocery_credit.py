from policyengine_us.model_api import *


class id_grocery_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho base grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        person = tax_unit.members

        # Incarcerated people are not eligible for the grocery credit
        incarcerated = person("is_incarcerated", period)
        total_incacerated = tax_unit.sum(incarcerated)
        # Each person in the tax unit is eligible for the base grocery credit
        tax_unit_size = tax_unit("tax_unit_size", period)
        tax_unit_size_less_incarcerated = max_(
            tax_unit_size - total_incacerated, 0
        )
        p = parameters(period).gov.states.id.tax.income.credits.grocery.amount
        base_credit = tax_unit_size_less_incarcerated * p.base
        # Aged head and spouse are eligible for an additional grocery credit amount
        age = person("age", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible_aged = head_or_spouse * ~incarcerated
        aged_amount = p.aged.calc(age)
        return base_credit + tax_unit.sum(eligible_aged * aged_amount)
