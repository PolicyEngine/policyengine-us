from openfisca_us.model_api import *


class ctc_reducible_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC reducible income tax liability"
    unit = "currency-USD"
    documentation = (
        "Income Tax liability which the non-refundable CTC can reduce."
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        tax_liability = tax_unit("income_tax_before_credits", period)
        OTHER_CREDITS = [
            "residential_energy_credit",
            "foreign_tax_credit",
            "child_dependent_care_expense_credit",
            "education_tax_credits",
            "retirement_savings_credit",
            "elderly_disabled_credit",
        ]
        credits = add(tax_unit, period, OTHER_CREDITS)
        return max_(tax_liability - credits, 0)


class ctc_max_refundable_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC maximum refundable amount"
    unit = "currency-USD"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        child_max = tax_unit("ctc_child_maximum", period)
        adult_max = tax_unit("ctc_adult_maximum", period)
        max_ctc = child_max + adult_max
        percent_reduction = tax_unit("ctc_percent_reduction", period)
        reducible_liability = tax_unit("ctc_reducible_income_tax", period)
        max_entitlement = max_ctc * (1 - percent_reduction)
        if ctc.refundable:
            return max_entitlement
        else:
            return min_(max_entitlement, reducible_liability)


class ctc_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC for child dependents"
    unit = "currency-USD"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        child_max = tax_unit("ctc_child_maximum", period)
        adult_max = tax_unit("ctc_adult_maximum", period)
        max_refundable_ctc = tax_unit("ctc_max_refundable_amount", period)
        return child_max / (child_max + adult_max) * max_refundable_ctc


c07220 = variable_alias("c07220", ctc_child)


class ctc_adult(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC for adult dependents"
    unit = "currency-USD"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        child_max = tax_unit("ctc_child_maximum", period)
        adult_max = tax_unit("ctc_adult_maximum", period)
        max_refundable_ctc = tax_unit("ctc_max_refundable_amount", period)
        return adult_max / (child_max + adult_max) * max_refundable_ctc


odc = variable_alias("odc", ctc_adult)


class nonrefundable_ctc_unclaimable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Non-refundable CTC unclaimable"
    unit = "currency-USD"
    documentation = "Value of CTC not payable due to non-refundability."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        maximum_ctc = add(
            tax_unit, period, ["ctc_child_maximum", "ctc_adult_maximum"]
        )
        percent_reduction = tax_unit("ctc_percent_reduction", period)
        ctc_if_fully_refundable = maximum_ctc * (1 - percent_reduction)
        return ctc_if_fully_refundable - tax_unit("child_tax_credit", period)


codtc_limited = variable_alias("codtc_limited", nonrefundable_ctc_unclaimable)
