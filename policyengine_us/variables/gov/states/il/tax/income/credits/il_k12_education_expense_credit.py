from policyengine_us.model_api import *


class il_k12_education_expense_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois K-12 Education Expense Credit"
    unit = USD
    definition_period = YEAR

    defined_for = "il_is_exemption_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.credits.k12
        tuition_and_fees = tax_unit("k12_tuition_and_fees", period)
        reduced_tuition_and_fees = max_(0, tuition_and_fees - p.reduction)
        k12_credit = min_(reduced_tuition_and_fees * p.rate, p.cap)
        pre_credit_tax = tax_unit(
            "il_income_tax_before_non_refundable_credits", period
        )
        il_property_tax_credit = tax_unit("il_property_tax_credit", period)
        avail_tax = max_(0, pre_credit_tax - il_property_tax_credit)
        return min_(avail_tax, k12_credit)
