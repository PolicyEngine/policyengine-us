from policyengine_us.model_api import *


class dc_medicaid_eligible(Variable):
    value_type = bool
    entity = Person
    label = "DC Medicaid eligible"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = [
        "https://dhcf.dc.gov/medicaid",
        "https://code.dccouncil.gov/us/dc/council/code/sections/1-307.02",
    ]

    def formula(person, period, parameters):
        # DC-specific eligibility for those not covered by federal Medicaid
        # This includes undocumented immigrants and others through the Alliance program
        immigration_eligible = person("dc_medicaid_immigration_eligible", period)
        income_eligible = person("dc_medicaid_income_eligible", period)
        age_eligible = person("dc_medicaid_age_eligible", period)

        # Person is eligible if they meet all DC-specific criteria
        # Note: immigration_eligible already filters to those NOT federally eligible
        return immigration_eligible & income_eligible & age_eligible