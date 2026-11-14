from policyengine_us.model_api import *


class ar_homestead_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    default_value = 0
    defined_for = "ar_homestead_property_tax_credit_eligible"
    label = "Arkansas Homestead Property Tax Credit for the assessment year"
    # PDF pages 1-2 for each act; assessment year precedes ordinary collection.
    reference = (
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2025R%2FPublic%2FACT330.pdf#page=1",
        "https://arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2026F%2FPublic%2FACT174.pdf#page=1",
    )

    # Assessment years before 2025 are unsupported, with numeric default 0.
    # This bill credit is diagnostic; it is not an additional cash payment.
    def formula_2025_01_01(tax_unit, period, parameters):
        p = parameters(period).gov.states.ar.tax.property.homestead_property_tax_credit
        qualified_property_taxes = tax_unit(
            "ar_homestead_property_tax_credit_qualified_property_taxes", period
        )
        return min_(qualified_property_taxes, p.maximum)
