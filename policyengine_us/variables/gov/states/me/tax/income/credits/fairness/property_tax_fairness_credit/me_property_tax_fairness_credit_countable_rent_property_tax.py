from policyengine_us.model_api import *


class me_property_tax_fairness_credit_countable_rent_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = (
        "Countable rent property tax for Maine property tax fairness credit"
    )
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        rent = add(tax_unit, period, ["rent"])
        ptax = add(tax_unit, period, ["real_estate_taxes"])
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.property_tax
        utilities_included_in_rent = tax_unit(
            "utilities_included_in_rent", period
        )
        utility_expenses = add(tax_unit, period, ["utility_expense"])
        # A separate calcuation exists for the case where utilities are included in rent
        # if the filer does not know the portion of rent that is attributable to utilities
        # This is not implemented
        applicable_rent_amount = where(
            utilities_included_in_rent,
            rent - utility_expenses,
            rent,
        )
        applicable_rent = applicable_rent_amount * p.rate.rent
        return applicable_rent + ptax
