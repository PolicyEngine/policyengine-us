from policyengine_us.model_api import *


class tx_school_district_homestead_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Texas school district residence homestead exemption"
    definition_period = YEAR
    reference = "https://comptroller.texas.gov/taxes/property-tax/exemptions/"
    defined_for = StateCode.TX

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["assessed_property_value"]) > 0
