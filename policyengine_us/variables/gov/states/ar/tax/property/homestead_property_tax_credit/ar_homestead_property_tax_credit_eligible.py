from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    defined_for = "ar_homestead_property_tax_credit_inputs_available"
    label = "Eligible for the Arkansas Homestead Property Tax Credit"
    reference = (
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2023R%2FPublic%2FACT541.pdf#page=1",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2001%2FPublic%2FACT1544.pdf#page=1",
    )

    def formula_2025_01_01(tax_unit, period, parameters):
        property_in_arkansas = tax_unit(
            "ar_homestead_property_tax_credit_property_in_arkansas", period
        )
        homestead_qualified = tax_unit(
            "ar_homestead_property_tax_credit_homestead_qualified", period
        )
        registered = tax_unit("ar_homestead_property_tax_credit_registered", period)
        claimant = tax_unit("ar_homestead_property_tax_credit_claimant", period)
        claims_exemption = tax_unit(
            "ar_homestead_property_tax_credit_claims_disabled_veteran_exemption",
            period,
        )
        return (
            property_in_arkansas
            & homestead_qualified
            & registered
            & claimant
            & ~claims_exemption
        )
