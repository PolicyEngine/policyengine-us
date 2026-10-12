from policyengine_us.model_api import *


class tx_school_district_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Texas school district residence homestead exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://statutes.capitol.texas.gov/Docs/TX/htm/TX.11.htm#11.13",
        "https://comptroller.texas.gov/taxes/property-tax/exemptions/",
    )
    defined_for = "tx_school_district_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        return min_(
            add(tax_unit, period, ["assessed_property_value"]),
            parameters(
                period
            ).gov.states.tx.tax.property.school_district_homestead_exemption.general_amount,
        )
