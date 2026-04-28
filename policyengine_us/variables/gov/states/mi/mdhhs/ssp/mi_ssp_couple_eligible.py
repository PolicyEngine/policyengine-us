from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mi.mdhhs.ssp.mi_ssp_living_arrangement import (
    MISSPLivingArrangement,
)


class mi_ssp_couple_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Michigan SSP couple rate applies"
    definition_period = MONTH
    defined_for = "mi_ssp_eligible"
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=4",
    )

    def formula(person, period, parameters):
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        eligible = person("mi_ssp_eligible", period)
        both_eligible = person.marital_unit.sum(eligible) == 2
        living_arrangement = person("mi_ssp_living_arrangement", period)
        qualifying_arrangements = [
            MISSPLivingArrangement.INDEPENDENT_LIVING,
            MISSPLivingArrangement.HOUSEHOLD_OF_ANOTHER,
            MISSPLivingArrangement.DOMICILIARY_CARE,
            MISSPLivingArrangement.PERSONAL_CARE,
            MISSPLivingArrangement.HOME_FOR_AGED,
            MISSPLivingArrangement.INSTITUTION,
        ]
        both_same_arrangement = (
            sum(
                person.marital_unit.sum(living_arrangement == value) == 2
                for value in qualifying_arrangements
            )
            > 0
        )
        return joint_claim & both_eligible & both_same_arrangement
