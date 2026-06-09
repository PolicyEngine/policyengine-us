from policyengine_us.model_api import *


class ia_cca_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Iowa CCA"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=3"

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["ia_cca_eligible_child"]) > 0
        asset_eligible = spm_unit("ia_cca_asset_eligible", period)
        income_eligible = spm_unit("ia_cca_income_eligible", period)
        activity_eligible = spm_unit("ia_cca_activity_eligible", period)
        # Families eligible without regard to income (FIP, protective,
        # foster) bypass both the income test and the activity need-for-
        # service test (IAC 441-170.2(1)"b").
        income_exception = spm_unit("ia_cca_income_exception", period)
        standard_path = income_eligible & activity_eligible
        return has_eligible_child & asset_eligible & (standard_path | income_exception)
