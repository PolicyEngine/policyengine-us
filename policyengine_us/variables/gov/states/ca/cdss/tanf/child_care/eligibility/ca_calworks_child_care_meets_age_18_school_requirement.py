from policyengine_us.model_api import *


class ca_calworks_child_care_meets_age_18_school_requirement(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    defined_for = StateCode.CA
    label = "California CalWORKs child-care age-18 school requirement"
    documentation = "Whether this 18-year-old meets MPP 42-101.2: enrolled full time in high school, or before high-school completion in a non-college-degree vocational/technical program, expected to complete before age 19. Correspondence coursework does not qualify."
    reference = "https://www.cdss.ca.gov/ord/entres/getinfo/pdf/4EAS.pdf#page=43"
