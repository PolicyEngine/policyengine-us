from policyengine_us.model_api import *


class is_ny_medicaid_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for New York state-funded Medicaid by immigration status"
    definition_period = YEAR
    reference = (
        "https://www.health.ny.gov/health_care/medicaid/publications/gis/18ma005.htm",
        "https://www.cms.gov/files/document/ny-1332-waiver_updated-application12182023.pdf#page=24",
        "https://info.nystateofhealth.ny.gov/sites/default/files/June%20Webinar%20-%20NY%20State%20of%20Health%20Changes%20for%202026.pdf#page=15",
    )
    documentation = """
    New York gives state-funded Medicaid to residents it treats as
    permanently residing under color of law, Deferred Action for Childhood
    Arrivals recipients among them. The Essential Plan covered those
    recipients from August 1, 2024 to June 30, 2026. This variable is
    YEAR-defined and reads the status list at January 1, so the model
    applies the Medicaid route through 2024 and again from 2027.
    """
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.hhs.medicaid
        immigration_status = person("immigration_status", period)
        return np.isin(
            immigration_status.decode_to_str(),
            p.state_funded_immigration_statuses,
        )
