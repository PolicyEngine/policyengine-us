from policyengine_us.model_api import *


class me_ssp(Variable):
    value_type = float
    entity = Person
    label = "Maine State Supplemental Income Program"
    unit = USD
    definition_period = MONTH
    defined_for = "me_ssp_eligible"
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/content/assets/144c332-appendices-charts.docx",
        "https://legislature.maine.gov/statutes/22/title22sec3271.html",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/me.html",
    )

    def formula(person, period, parameters):
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        eligible = person("me_ssp_eligible", period)
        both_eligible = person.marital_unit.sum(eligible) == 2
        category = person("me_ssp_payment_category", period)
        # Both spouses must share the same payment category to be treated
        # as a joint couple claim.
        shared_category = person.marital_unit.max(category) == person.marital_unit.min(
            category
        )
        couple_applies = joint_claim & both_eligible & shared_category
        return where(
            couple_applies,
            person("me_ssp_couple", period),
            person("me_ssp_individual", period),
        )
