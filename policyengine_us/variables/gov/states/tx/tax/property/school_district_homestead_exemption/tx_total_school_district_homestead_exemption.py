from policyengine_us.model_api import *


class tx_total_school_district_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Texas total school district residence homestead exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://comptroller.texas.gov/taxes/property-tax/exemptions/"
    defined_for = "tx_school_district_homestead_exemption_eligible"
    adds = [
        "tx_school_district_homestead_exemption",
        "tx_over_65_or_disabled_school_district_homestead_exemption",
    ]
