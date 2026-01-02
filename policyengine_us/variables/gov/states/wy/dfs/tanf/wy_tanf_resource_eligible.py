from policyengine_us.model_api import *


class wy_tanf_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wyoming TANF resource eligible"
    definition_period = MONTH
    reference = (
        "https://codes.findlaw.com/wy/title-42-welfare/wy-st-sect-42-2-103.html",
        "https://dfs.wyo.gov/assistance-programs/cash-assistance/cash-assistance-income-and-resource-requirements/",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.tanf.eligibility.resources
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.limit
