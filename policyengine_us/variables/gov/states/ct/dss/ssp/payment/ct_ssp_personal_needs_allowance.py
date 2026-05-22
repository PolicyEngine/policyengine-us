from policyengine_us.model_api import *


class ct_ssp_personal_needs_allowance(Variable):
    value_type = float
    entity = Person
    label = "Connecticut SSP personal needs allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/fact-sheets-and-issue-briefs/fact-sheets/dss-program-standards-chart-effective-010126.pdf",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ct.dss.ssp
        arrangement = person("ct_ssp_living_arrangement", period.this_year)
        arrangements = arrangement.possible_values
        is_joint_claim = person("ssi_claim_is_joint", period.this_year)

        base_pna = p.personal_needs_allowance[arrangement]
        is_community = (arrangement == arrangements.COMMUNITY_ALONE) | (
            arrangement == arrangements.COMMUNITY_SHARED
        )
        return where(
            is_community & is_joint_claim,
            p.personal_needs_allowance_married,
            base_pna,
        )
