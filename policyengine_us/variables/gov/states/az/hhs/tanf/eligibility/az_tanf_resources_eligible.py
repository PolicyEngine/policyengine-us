from policyengine_us.model_api import *


class az_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arizona TANF resources eligible"
    definition_period = MONTH
    reference = (
        "https://az.db101.org/az/programs/income_support/tanf/program2.htm"
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.hhs.tanf.resources
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= p.limit
