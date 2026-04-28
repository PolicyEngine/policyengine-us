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
        # Categorical SSI eligibility (aged/blind/disabled + resources +
        # immigration). Income spillover is handled in mi_ssp_person via
        # the uncapped_ssi reduction per SSA 2011 baseline: countable
        # income deducts from federal SSI first; any remaining countable
        # income reduces the state supplement. Using is_ssi_eligible
        # (not ssi > 0) keeps the partial-SSP population in scope for
        # facility-care arrangements where the state supplement adds on
        # top of the federal FBR.
        # We don't track section 1619 working-disabled status at the moment.
        is_ssi_eligible = person("is_ssi_eligible", period.this_year)
        category = person("mi_ssp_payment_category", period)
        in_qualifying_arrangement = category != MISSPLivingArrangement.NONE
        return is_ssi_eligible & in_qualifying_arrangement
