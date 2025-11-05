from policyengine_us.model_api import *


class ga_tanf_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Georgia TANF assistance unit size"
    definition_period = MONTH
    reference = ("https://pamms.dhs.ga.gov/dfcs/tanf/appendix-a/",)
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        return spm_unit.nb_persons()
