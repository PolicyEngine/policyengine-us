from policyengine_us.model_api import *


class or_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oregon TANF countable resources"
    unit = USD
    definition_period = YEAR
    reference = "https://oregon.public.law/rules/oar_461-160-0015"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        return spm_unit("spm_unit_assets", period)
