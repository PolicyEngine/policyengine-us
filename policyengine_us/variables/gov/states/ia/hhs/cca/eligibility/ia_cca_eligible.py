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
        # foster) skip the income test (IAC 441-170.2(1)"b") and satisfy
        # the need-for-service requirement through their qualifying
        # condition: protective child care and licensed foster care are
        # themselves needs for service (IAC 441-170.2(2)"b"(3) and (9)),
        # and a FIP family qualifies through employment with no
        # minimum-hours requirement, education, or PROMISE JOBS
        # participation (IAC 441-170.2(2)"b"(6)-(7)) — we don't track
        # PROMISE JOBS participation at the moment, so FIP enrollment
        # serves as the proxy for need.
        income_exception = spm_unit("ia_cca_income_exception", period)
        standard_path = income_eligible & activity_eligible
        return has_eligible_child & asset_eligible & (standard_path | income_exception)
