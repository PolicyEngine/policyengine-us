from policyengine_us.model_api import *


class ca_ffyp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the California Former Foster Youth Program"
    definition_period = YEAR
    reference = (
        "https://www.dhcs.ca.gov/services/medi-cal/eligibility/Pages/FFY_Bene.aspx",
        "https://www.dhcs.ca.gov/formsandpubs/forms/Forms/MCED/MC_Forms/MC250A_Eng.pdf",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.dhcs.ffyp
        age = person("age", period)
        age_eligible = (age > p.foster_care_age_minimum) & (
            age < p.age_threshold
        )  # Person must be below age limit and previously in foster care for a valid age
        was_in_foster_care = person(
            "was_in_foster_care", period
        )  # Assumes the person was in foster care for a valid age
        return age_eligible & was_in_foster_care
