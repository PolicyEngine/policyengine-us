from policyengine_us.model_api import *


class ia_tanf_fip_family_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Iowa FIP family size"
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.28"
    documentation = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        return spm_unit.nb_persons()
