from policyengine_us.model_api import *


class pa_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "Pennsylvania TANF (Temporary Assistance for Needy Families)"
    documentation = "Monthly Pennsylvania TANF cash assistance benefit amount. TANF provides temporary cash assistance to families with children. Pennsylvania issues payments in two increments per month. https://www.pa.gov/agencies/dhs/resources/cash-assistance/tanf"

    def formula(spm_unit, period, parameters):
        return spm_unit("pa_tanf_benefit_amount", period)
