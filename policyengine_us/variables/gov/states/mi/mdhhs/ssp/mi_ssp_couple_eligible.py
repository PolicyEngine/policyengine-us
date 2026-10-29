from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)
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
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=1",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=4",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/248.pdf#page=2",
    )

    def formula(person, period, parameters):
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        eligible = person("mi_ssp_eligible", period)
        both_eligible = (
            _ssi_couple_total(person, period.this_year, eligible.astype(int)) == 2
        )
        category = person("mi_ssp_payment_category", period)
        spouse = _ssi_spouse_index(person, period.this_year)
        both_same_arrangement = (category != MISSPLivingArrangement.NONE) & (
            category == category[np.maximum(spouse, 0)]
        )
        return joint_claim & both_eligible & both_same_arrangement
