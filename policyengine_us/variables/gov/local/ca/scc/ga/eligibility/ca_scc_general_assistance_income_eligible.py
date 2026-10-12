from policyengine_us.model_api import *


class ca_scc_general_assistance_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Santa Clara County General Assistance based on income requirements"
    defined_for = "in_scc"
    reference = "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/01Policy/Policy.htm"

    def formula(spm_unit, period, parameters):
        income = spm_unit("ca_scc_general_assistance_countable_income", period)
        limit = spm_unit("ca_scc_general_assistance_base_amount", period)
        return income <= limit
