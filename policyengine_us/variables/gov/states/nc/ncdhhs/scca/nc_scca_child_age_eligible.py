from policyengine_us.model_api import *


class nc_scca_child_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "North Carolina child age eligibility for Subsidized Child Care Assistance (SCCA) program"
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/Chapter-4-RED-CN-26-03-Application-Eligibility-Determination-Documentation-2.pdf#page=10",
        "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83",
    )
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.scca.age.limit

        is_disabled = person("is_disabled", period)
        age = person("age", period)

        court_supervision = person("is_under_court_supervision", period)
        # Chapter 4 IX(ii)(b): a child under court-ordered supervision shares
        # the special-needs age limit.
        age_limit = where(is_disabled | court_supervision, p.disabled, p.non_disabled)

        return age < age_limit
