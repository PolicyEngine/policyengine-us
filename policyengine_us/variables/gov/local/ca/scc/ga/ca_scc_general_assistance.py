from policyengine_us.model_api import *


class ca_scc_general_assistance(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Santa Clara County General Assistance"
    defined_for = "ca_scc_general_assistance_eligible"
    reference = "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/01Policy/Policy.htm"

    def formula(spm_unit, period, parameters):
        base = spm_unit("ca_scc_general_assistance_base_amount", period)
        countable = spm_unit("ca_scc_general_assistance_countable_income", period)
        return base - max_(countable, 0)
