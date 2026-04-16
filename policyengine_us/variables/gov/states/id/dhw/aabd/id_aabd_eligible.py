from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.id.dhw.aabd.id_aabd_living_arrangement import (
    IDAAbdLivingArrangement,
)


class id_aabd_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Idaho AABD eligible"
    definition_period = MONTH
    defined_for = StateCode.ID
    reference = (
        "https://adminrules.idaho.gov/rules/current/16/160305.pdf#page=41",
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.05.514",
    )

    def formula(person, period, parameters):
        receives_ssi = person("ssi", period) > 0
        la = person("id_aabd_living_arrangement", period)
        LA = IDAAbdLivingArrangement
        # Nursing facility residents excluded (Section 501)
        federal_la = person("ssi_federal_living_arrangement", period.this_year)
        not_in_medical = (
            federal_la != federal_la.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        return receives_ssi & not_in_medical & (la != LA.RALF_CFH) & (la != LA.NONE)
