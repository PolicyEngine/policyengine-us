from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.id.dhw.aabd.id_aabd_living_arrangement import (
    IDAAbdLivingArrangement,
)


class id_aabd_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Idaho AABD eligible"
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://adminrules.idaho.gov/rules/current/16/160305.pdf#page=41",
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.05.514",
    )

    def formula(person, period, parameters):
        receives_ssi = person("ssi", period) > 0
        living_arrangement = person("id_aabd_living_arrangement", period)
        not_in_ralf_cfh = living_arrangement != IDAAbdLivingArrangement.RALF_CFH
        not_none = living_arrangement != IDAAbdLivingArrangement.NONE
        return receives_ssi & not_in_ralf_cfh & not_none
