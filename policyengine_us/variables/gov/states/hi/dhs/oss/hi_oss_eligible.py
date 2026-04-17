from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.hi.dhs.oss.hi_oss_living_arrangement import (
    HIOSSLivingArrangement,
)


class hi_oss_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person is eligible for Hawaii OSS"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = (
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415200SF",
        "https://secure.ssa.gov/POMS.NSF/lnx/0501415057",
    )

    def formula(person, period, parameters):
        # Per POMS SI 01401.001, "state supplement only" cases have
        # countable income above the FBR but below the combined
        # payment level. They receive $0 federal SSI but still
        # qualify for a reduced state supplement. Eligibility is
        # therefore categorical (is_ssi_eligible), not ssi > 0.
        is_eligible = person("is_ssi_eligible", period.this_year)
        living_arrangement = person("hi_oss_living_arrangement", period)
        in_qualifying_facility = living_arrangement != HIOSSLivingArrangement.NONE
        return is_eligible & in_qualifying_facility
