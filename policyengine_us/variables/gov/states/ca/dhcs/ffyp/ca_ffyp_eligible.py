from policyengine_us.model_api import *


class ca_ffyp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for California Former Foster Youth Program"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dhcs.ca.gov/services/medi-cal/eligibility/Pages/FFY_Bene.aspx"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.dhcs.ffyp
        age = person("age", period)
        age_eligible = (
            p.foster_care_age_minimum < age < p.age_limit
        )  # Person must be below age limit and previously in foster care for a valid age
        if ~age_eligible:
            return False  # Person automatically ineligible if not within age bounds
        age_gap_from_minimum = (
            age - p.foster_care_age_minimum
        )  # Find the number of possible years the person could have been in foster care
        head = period
        for _ in range(age_gap_from_minimum + 1):
            if person("was_in_foster_care", head):
                return True  # Person eligible if age eligible and in foster care for a valid year
            head = (
                head.last_year
            )  # If not eligible yet, check the previous year
        return False
