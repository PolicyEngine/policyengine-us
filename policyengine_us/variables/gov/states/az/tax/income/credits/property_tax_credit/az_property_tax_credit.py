from policyengine_us.model_api import *


class az_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Property Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "az_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.az.tax.income.credits.property_tax
        income = tax_unit("az_property_tax_credit_income", period)

        cohabitating = tax_unit("cohabitating_spouses", period)

        cap = where(
            cohabitating,
            p.amount.cohabitating.calc(income),
            p.amount.living_alone.calc(income),
        )

        # Rent counts equally to property taxes.
        property_tax_plus_rent = add(
            tax_unit, period, ["real_estate_taxes", "rent"]
        )
        # property_tax and rent are equally weighted

        return min_(cap, property_tax_plus_rent)
