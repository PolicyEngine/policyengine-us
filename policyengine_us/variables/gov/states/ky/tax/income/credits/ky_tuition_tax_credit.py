from policyengine_us.model_api import *


class ky_tuition_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky tuition tax credits (from Form 8863-K)"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        tentative_tax_credit = add(
            tax_unit,
            period,
            ["american_opportunity_credit", "lifetime_learning_credit"],
        )
        rate = parameters(
            period
        ).gov.states.ky.tax.income.credits.tuition_tax.rate
        tuition_credit = tentative_tax_credit * rate
        tax_before_non_refundable = tax_unit(
            "ky_income_tax_before_non_refundable_credits", period
        )
        return min_(tax_before_non_refundable, tuition_credit)
