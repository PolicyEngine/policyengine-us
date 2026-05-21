from policyengine_us.model_api import *


class az_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Arizona Child Care Assistance Program"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/services/child-and-family/child-care/how-apply-for-child-care-assistance",
        "https://des.az.gov/sites/default/files/dl/CCA-1227A.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.az.hhs.ccap.eligibility
        age = person("age", period.this_year)
        attending_days = person("childcare_attending_days_per_month", period.this_year)
        return (age < p.child_age_limit) & (attending_days > 0)
