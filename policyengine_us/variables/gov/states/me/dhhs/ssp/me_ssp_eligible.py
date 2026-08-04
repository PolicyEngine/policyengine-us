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
        # Part 11 covers SSI recipients AND people who would qualify for
        # SSI except for income (Chart 3.6's State Supplement-only path).
        # `is_ssi_eligible` checks aged/blind/disabled, resource, and
        # immigration but NOT income, so it captures both groups. The
        # but-for-citizenship pathway is not modeled because we don't
        # track the 8/96 immigration category at the moment.
        categorically_eligible = person("is_ssi_eligible", period)
        category = person("me_ssp_payment_category", period)
        in_qualifying_category = category != category.possible_values.NONE
        return categorically_eligible & in_qualifying_category
