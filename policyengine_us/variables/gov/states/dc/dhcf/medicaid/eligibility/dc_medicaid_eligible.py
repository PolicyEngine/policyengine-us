from policyengine_us.model_api import *


class dc_medicaid_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for DC Medicaid/Alliance"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = [
        "https://dhcf.dc.gov/alliance",
        "https://code.dccouncil.gov/us/dc/council/code/sections/1-307.02",
    ]
    documentation = """
    DC Health Care Alliance provides coverage to immigrants who are not
    eligible for federal Medicaid due to their immigration status.
    This includes undocumented immigrants, DACA recipients, and TPS holders.
    """

    def formula(person, period, parameters):
        # DC Alliance is for immigrants not covered by federal Medicaid
        # Must have a DC-covered immigration status (undocumented, DACA, TPS)
        immigration_status_covered = person(
            "dc_medicaid_immigration_status_eligible", period
        )
        income_eligible = person("dc_medicaid_income_eligible", period)
        age_eligible = person("dc_medicaid_age_eligible", period)

        return immigration_status_covered & income_eligible & age_eligible
