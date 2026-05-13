from policyengine_us.model_api import *


class is_basic_health_program_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible immigration status for Basic Health Program coverage"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/600.305",
        "https://www.law.cornell.edu/cfr/text/45/155.20",
        "https://www.federalregister.gov/documents/2024/05/08/2024-09661/clarifying-the-eligibility-of-deferred-action-for-childhood-arrivals-daca-recipients-and-certain",
        "https://www.federalregister.gov/documents/2025/06/25/2025-11606/patient-protection-and-affordable-care-act-marketplace-integrity-and-affordability",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.basic_health_program.eligibility
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        ineligible_immigration_status = np.isin(
            immigration_status_str, p.ineligible_immigration_statuses
        )
        return ~ineligible_immigration_status
