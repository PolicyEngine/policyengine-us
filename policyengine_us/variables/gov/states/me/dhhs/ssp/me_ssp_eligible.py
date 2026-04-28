from policyengine_us.model_api import *


class me_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Maine State Supplemental Income Program"
    definition_period = MONTH
    defined_for = StateCode.ME
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://legislature.maine.gov/statutes/22/title22sec3271.html",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/me.html",
    )

    def formula(person, period, parameters):
        # Part 11 §1: "the individual must be receiving SSI." `ssi > 0`
        # already implies categorical (ABD), resource, immigration, the
        # federal income test, and takeup. The non-SSI but-for-income
        # and 8/96-citizenship pathways are not modeled because we
        # don't track income-in-kind or the 8/96 immigration category
        # at the moment.
        receives_ssi = person("ssi", period) > 0
        category = person("me_ssp_payment_category", period)
        in_qualifying_category = category != category.possible_values.NONE
        return receives_ssi & in_qualifying_category
