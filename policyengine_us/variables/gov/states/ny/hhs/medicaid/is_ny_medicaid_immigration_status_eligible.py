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
    Arrivals recipients among them. The Essential Plan was due to take
    those aged 19 to 64 with income up to 250% of the poverty level from
    August 1, 2024, so from then on this route covers DACA recipients
    under 19 or aged 65 or older. This variable is YEAR-defined and reads
    its parameters at January 1, so every DACA recipient passes through
    2024. The model does not apply the return of some adults to Medicaid
    on July 1, 2026.
    """
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.hhs.medicaid
        immigration_status = person("immigration_status", period)
        state_funded_status = np.isin(
            immigration_status.decode_to_str(),
            p.state_funded_immigration_statuses,
        )
        # The Essential Plan was due to take DACA recipients aged 19 to 64
        # with income up to 250% of the poverty level. The test reads age
        # alone, because Essential Plan eligibility itself reads Medicaid.
        daca = immigration_status == immigration_status.possible_values.DACA
        age = person("age", period)
        in_essential_plan_ages = p.daca_in_essential_plan.calc(age).astype(bool)
        return state_funded_status & ~(daca & in_essential_plan_ages)
