from policyengine_us.model_api import *


class tx_over_65_or_disabled_school_district_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Texas age 65 or older or disabled school district residence homestead exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://comptroller.texas.gov/taxes/property-tax/exemptions/"
    defined_for = "tx_over_65_or_disabled_school_district_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        remaining_value = max_(
            add(tax_unit, period, ["assessed_property_value"])
            - tax_unit("tx_school_district_homestead_exemption", period),
            0,
        )
        return min_(
            remaining_value,
            parameters(
                period
            ).gov.states.tx.tax.property.school_district_homestead_exemption.over_65_or_disabled_amount,
        )
