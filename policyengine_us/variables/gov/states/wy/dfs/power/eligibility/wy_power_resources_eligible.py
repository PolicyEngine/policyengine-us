from policyengine_us.model_api import *


class wy_power_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wyoming POWER resources eligible"
    definition_period = MONTH
    reference = (
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/table-ii-power-income-limits/",
        "https://dfs.wyo.gov/assistance-programs/cash-assistance/cash-assistance-income-and-resource-requirements/",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.power.resources
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.limit
