from policyengine_us.model_api import *


class il_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL Property Tax Credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        property_tax = tax_unit("property_tax_primary_residence", period)
        qbid = tax_unit("qualified_business_income_deduction", period)
        income_tax_before_credits = tax_unit(
            "il_income_tax_before_nonrefundable_credits", period
        )
        rate = parameters(
            period
        ).gov.states.il.tax.income.credits.property_tax.rate

        return min_((property_tax - qbid) * rate, income_tax_before_credits)
