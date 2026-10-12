from policyengine_us.model_api import *


class az_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Arizona Child Care Assistance Program"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/services/child-and-family/child-care/how-apply-for-child-care-assistance",
        "https://des.az.gov/sites/default/files/dl/CCA-1227A.pdf",
        "https://www.law.cornell.edu/cfr/text/45/98.20",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.az.hhs.ccap.eligibility
        age = person("age", period.this_year)
        attending_days = person("childcare_attending_days_per_month", period.this_year)
        # AZ defines an eligible child as "a child less than 13 years of age"
        # (R6-5-4901(27)) for all children; there is no higher ceiling for disabled
        # children (the Special Needs Rate itself is birth-through-12 on CCA-1227A),
        # so we don't model a 13-17 special-needs age extension.
        # CCDF (45 CFR 98.20) requires the child to be a citizen or qualified
        # noncitizen, consistent with every other state CCAP implementation.
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return (age < p.child_age_limit) & (attending_days > 0) & immigration_eligible
