from policyengine_us.model_api import *


class pa_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF"
    unit = USD
    definition_period = MONTH
    defined_for = "pa_tanf_eligible"
    reference = (
        "https://www.pa.gov/agencies/dhs/resources/cash-assistance/tanf"
    )

    def formula(spm_unit, period, parameters):
        maximum_benefit = spm_unit("pa_tanf_maximum_benefit", period)
        countable_income = spm_unit("pa_tanf_countable_income", period)

        return max_(maximum_benefit - countable_income, 0)
