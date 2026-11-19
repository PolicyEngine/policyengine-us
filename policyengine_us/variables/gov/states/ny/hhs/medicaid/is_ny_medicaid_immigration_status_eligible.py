from policyengine_us.model_api import *


class is_ny_medicaid_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for New York state-funded Medicaid by immigration status"
    definition_period = YEAR
    reference = (
        "https://www.cms.gov/files/document/ny-1332-waiver_updated-application12182023.pdf#page=24",
        "https://www.cms.gov/files/document/ny-1332-waiver_updated-application12182023.pdf#page=25",
    )
    documentation = """
    New York gives state-funded Medicaid to residents it treats as
    permanently residing under color of law, Deferred Action for Childhood
    Arrivals recipients among them. This variable is YEAR-defined and reads
    the status list at January 1, so the August 1, 2024 move of those
    recipients to the Essential Plan applies in the model from 2025.
    """
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.hhs.medicaid
        immigration_status = person("immigration_status", period)
        return np.isin(
            immigration_status.decode_to_str(),
            p.state_funded_immigration_statuses,
        )
