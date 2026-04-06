from policyengine_us.model_api import *


class meets_ssi_resource_test(Variable):
    value_type = bool
    entity = Person
    label = "Meets SSI resource test"
    definition_period = YEAR
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501110000"

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi
        joint_claim = person("ssi_claim_is_joint", period)
        personal_resources = person("ssi_countable_resources", period)
        countable_resources = where(
            joint_claim,
            person.marital_unit.sum(personal_resources),
            personal_resources,
        )
        resource_limit = where(
            joint_claim,
            p.eligibility.resources.limit.couple,
            p.eligibility.resources.limit.individual,
        )
        return countable_resources <= resource_limit
