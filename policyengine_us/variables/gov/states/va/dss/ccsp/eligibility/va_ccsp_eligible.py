from policyengine_us.model_api import *


class va_ccsp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Virginia Child Care Subsidy Program"
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/admincode/title8/agency20/chapter790/section40/",
        "https://doe.virginia.gov/home/showpublisheddocument/56270#page=54",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        has_eligible_child = spm_unit.any(person("va_ccsp_child_eligible", period))
        income_eligible = spm_unit("va_ccsp_income_eligible", period)
        activity_eligible = spm_unit("va_ccsp_activity_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        return has_eligible_child & income_eligible & activity_eligible & asset_eligible
