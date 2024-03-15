from policyengine_us.model_api import *


class mi_homestead_property_tax_credit_countable_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan homestead property tax credit countable property tax (including rent equivalent)"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-520",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=1",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax
        # Line 10
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        # Line 11
        rent = add(tax_unit, period, ["rent"])
        # Line 12
        applicable_rent = rent * p.rent_equivalization
        # Line 13
        return property_tax + applicable_rent
