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
        deemed_resources = add(
            person,
            period,
            [
                "ssi_resources_deemed_from_ineligible_spouse",
                "ssi_resources_deemed_from_ineligible_parent",
            ],
        )
        countable_resources = where(
            joint_claim,
            person.marital_unit.sum(personal_resources),
            personal_resources + deemed_resources,
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
