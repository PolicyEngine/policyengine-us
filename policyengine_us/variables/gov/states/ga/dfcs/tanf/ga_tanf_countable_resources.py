from policyengine_us.model_api import *


class ga_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF countable resources"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://rules.sos.ga.gov/gac/290-2-28-.13",
        "https://pamms.dhs.ga.gov/dfcs/tanf/appendix-a/",
    )
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        # For simplicity, use the standard SPM unit assets
        # In a more complete implementation, this would account for
        # excluded resources and vehicle value limits
        assets = spm_unit("spm_unit_assets", period)
        return max_(assets, 0)
