from policyengine_us.model_api import *


class il_k12_education_expense_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL K-12 Education Expense Credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.credits.k12
        tuition_and_fees = tax_unit("k12_tuition_and_fees", period)
        reduced_tuition_and_fees = max_(0, tuition_and_fees - p.reduction)
        max_credit = reduced_tuition_and_fees * p.rate

        il_income_tax_before_nonrefundable_credits = tax_unit(
            "il_income_tax_before_nonrefundable_credits", period
        )
        il_property_tax_credit = tax_unit("il_property_tax_credit", period)

        return min_(
            il_income_tax_before_nonrefundable_credits
            - il_property_tax_credit,
            min_(max_credit, p.cap),
        )
