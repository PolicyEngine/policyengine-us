from policyengine_us.model_api import *


class de_aged_personal_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware aged additional personal credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.de.tax.income.credits.personal_credits

        # Legal code says "An additional $110 in the case of each resident person age 60 or over."
        # Tax form limits it to heads and spouses, not elderly dependents.

        age_head = tax_unit("age_head", period)
        head_amount = p.aged.calc(age_head)

        age_spouse = tax_unit("age_spouse", period)
        spouse_amount = p.aged.calc(age_spouse)

        return head_amount + spouse_amount
