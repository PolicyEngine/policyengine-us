from policyengine_us.model_api import *


class va_map_bccpta_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP BCCPTA eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    # can be eligible only if not eligible for another program 
    def formula(spm_unit, period, parameters):
        famis = spm_unit("va_map_famis_eligibility", period)
        pregnant = spm_unit("va_map_pregnant_eligibility", period)
        ssi = spm_unit("va_map_ssi_eligiblity", period)


        return 
