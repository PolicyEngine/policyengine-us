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
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=5",
    )

    def formula(person, period, parameters):
        # We don't track section 1619 working-disabled status at the moment.
        receives_ssi = person("ssi", period.this_year) > 0
        living_arrangement = person("mi_ssp_living_arrangement", period)
        in_qualifying_arrangement = living_arrangement != MISSPLivingArrangement.NONE
        return receives_ssi & in_qualifying_arrangement
