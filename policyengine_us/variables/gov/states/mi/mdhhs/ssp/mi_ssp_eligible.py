from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mi.mdhhs.ssp.mi_ssp_living_arrangement import (
    MISSPLivingArrangement,
)


class mi_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Michigan SSP eligible"
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=4",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=2",
    )

    def formula(person, period, parameters):
        # MDHHS-administered categories (Independent Living and Household
        # of Another) require an actual regular federal SSI check per BEM
        # 660.
        # SSA-administered Adult Foster Care (Domiciliary, Personal) and
        # Home for the Aged/Institution categories use categorical
        # eligibility plus the spillover reduction in mi_ssp_person, per
        # the SSA baseline: countable income deducts from federal SSI
        # first, and any remaining countable income reduces the state
        # supplement.
        # We don't track section 1619 working-disabled status at the moment.
        category = person("mi_ssp_payment_category", period)
        is_strict_category = (category == MISSPLivingArrangement.INDEPENDENT_LIVING) | (
            category == MISSPLivingArrangement.HOUSEHOLD_OF_ANOTHER
        )
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        is_ssi_eligible = person("is_ssi_eligible", period)
        arrangement_gate = where(
            is_strict_category,
            receives_ssi,
            is_ssi_eligible,
        )
        in_qualifying_arrangement = category != MISSPLivingArrangement.NONE
        return arrangement_gate & in_qualifying_arrangement
