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
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/248.pdf#page=2",
    )

    def formula(person, period, parameters):
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        eligible = person("mi_ssp_eligible", period)
        # Summing the same variable used in defined_for is safe here; if a
        # future contributor swaps to summing a different variable across
        # the marital unit, the defined_for filter could silently halve
        # the result.
        both_eligible = person.marital_unit.sum(eligible) == 2
        category = person("mi_ssp_payment_category", period)
        qualifying_arrangements = [
            value
            for value in MISSPLivingArrangement
            if value != MISSPLivingArrangement.NONE
        ]
        both_same_arrangement = (
            sum(
                person.marital_unit.sum(category == value) == 2
                for value in qualifying_arrangements
            )
            > 0
        )
        return joint_claim & both_eligible & both_same_arrangement
