from policyengine_us.model_api import *


class meets_ssi_resource_test(Variable):
    value_type = bool
    entity = Person
    label = "Meets SSI resource test"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202",
        "https://www.ecfr.gov/current/title-20/section-416.1205",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330110",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi
        joint_claim = person("ssi_claim_is_joint", period)
        personal_resources = person("ssi_countable_resources", period)
        spousal_deeming = person("is_ssi_spousal_resource_deeming_applies", period)
        spouse_resources = person("ssi_resources_deemed_from_ineligible_spouse", period)
        parent_resources = person("ssi_resources_deemed_from_ineligible_parent", period)
        # Balances are float32 inputs, so a sum of them can land a fraction of
        # a cent off the total it represents. Round each such sum to cents: a
        # couple's balances, or a person's own plus a spouse's. The parental
        # share is an equal division with no rounding rule (SI 01330.200 B,
        # 416.1202(b)(1)), so it is added unrounded.
        countable_resources = where(
            joint_claim,
            round_to_cents(person.marital_unit.sum(personal_resources)),
            round_to_cents(personal_resources + spouse_resources) + parent_resources,
        )
        # 416.1205(a): an individual living with an ineligible spouse counts
        # 'including the resources of the spouse' against the spouse limit.
        # This applies even when no income is deemed or the spouse owns zero.
        resource_limit = where(
            joint_claim | spousal_deeming,
            p.eligibility.resources.limit.couple,
            p.eligibility.resources.limit.individual,
        )
        return countable_resources <= resource_limit
