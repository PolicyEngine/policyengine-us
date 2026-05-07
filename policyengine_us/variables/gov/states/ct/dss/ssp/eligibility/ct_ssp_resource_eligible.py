from policyengine_us.model_api import *


class ct_ssp_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Connecticut SSP resource eligible"
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://www.ctdssmap.com/CTPortal/Information/Get/UPM#4005.10",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        # Per UPM 4005.10: CT asset limits ($1,600/$2,400) are lower than
        # federal SSI limits ($2,000/$3,000).
        p = parameters(period).gov.states.ct.dss.ssp.eligibility
        personal_resources = person("ssi_countable_resources", period.this_year)
        is_joint_claim = person("ssi_claim_is_joint", period.this_year)
        has_ineligible_spouse = (
            person.marital_unit.sum(
                person("is_ssi_ineligible_spouse", period.this_year)
            )
            > 0
        )
        applies_couple_limit = is_joint_claim | has_ineligible_spouse
        resources = where(
            applies_couple_limit,
            person.marital_unit.sum(personal_resources),
            personal_resources,
        )
        limit = where(
            applies_couple_limit,
            p.asset_limit.couple,
            p.asset_limit.individual,
        )
        return resources <= limit
