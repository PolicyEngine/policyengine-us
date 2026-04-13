from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class de_aged_personal_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware aged personal credit"
    unit = USD
    definition_period = YEAR
    reference = "https://delcode.delaware.gov/title30/c011/sc02/index.html#1110"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.de.tax.income.credits.personal_credits
        """
          Legal code says "An additional $110 in the case of each resident
          person age 60 or over.  Tax form limits it to heads and spouses,
          not elderly dependents.
        """
        age_head = tax_unit("age_head", period)
        head_amount = p.aged.calc(age_head)

        age_spouse = tax_unit("age_spouse", period)
        spouse_amount = p.aged.calc(age_spouse)

        return head_amount + spouse_amount


class de_aged_personal_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware aged personal credit"
    unit = USD
    definition_period = YEAR
    reference = "https://delcode.delaware.gov/title30/c011/sc02/index.html#1110"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.de.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "de_income_tax_before_non_refundable_credits_unit",
            "de_aged_personal_credit",
            "de_aged_personal_credit_potential",
        )
