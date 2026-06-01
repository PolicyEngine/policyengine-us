from policyengine_us.model_api import *


class ca_oc_general_relief_receives_other_cash_assistance(Variable):
    value_type = bool
    entity = Person
    label = "Receives other cash assistance that excludes Orange County General Relief"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2026-01/GR%20Reg%20SECTION%2020%20-%20Approved%20-%20January%202026.pdf#page=03"

    def formula(person, period, parameters):
        receives_ssi = person("ssi", period) > 0
        receives_calworks = person.spm_unit("ca_tanf", period) > 0
        return receives_ssi | receives_calworks
