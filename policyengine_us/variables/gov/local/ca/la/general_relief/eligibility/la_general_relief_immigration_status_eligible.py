from policyengine_us.model_api import *


class la_general_relief_immigration_status_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for the Los Angeles County General Relief based on the immigration status requirements"
    # Person has to be a resident of LA County
    defined_for = "in_la"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # Undocuemnted as well as DACA classified filers are ineligible for the GR
        istatus = person("immigration_status", period)
        daca_tps = istatus == istatus.possible_values.DACA_TPS
        undocumented = istatus == istatus.possible_values.UNDOCUMENTED
        # Assuming that the applicant's immigration status is recorded
        ineligible_status = daca_tps | undocumented
        return ~spm_unit.any(ineligible_status)
