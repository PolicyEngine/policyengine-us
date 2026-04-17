from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.hi.dhs.oss.hi_oss_living_arrangement import (
    HIOSSLivingArrangement,
)


class hi_oss_couple_rate_applies(Variable):
    value_type = bool
    entity = Person
    label = "Whether the Hawaii OSS couple rate applies"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = (
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415200SF",
        "https://secure.ssa.gov/POMS.NSF/lnx/0501415057",
    )

    def formula(person, period, parameters):
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        is_eligible = person("is_ssi_eligible", period.this_year)
        both_ssi_eligible = (
            person.marital_unit.sum(is_eligible) == person.marital_unit.nb_persons()
        )
        la = person("hi_oss_living_arrangement", period)
        LA = HIOSSLivingArrangement
        unit_size = person.marital_unit.nb_persons()
        both_same_facility = (
            (person.marital_unit.sum(la == LA.COMMUNITY_CARE) == unit_size)
            | (person.marital_unit.sum(la == LA.DOMICILIARY_CARE_I) == unit_size)
            | (person.marital_unit.sum(la == LA.DOMICILIARY_CARE_II) == unit_size)
            | (person.marital_unit.sum(la == LA.MEDICAID_INSTITUTION) == unit_size)
        )
        return joint_claim & both_ssi_eligible & both_same_facility
