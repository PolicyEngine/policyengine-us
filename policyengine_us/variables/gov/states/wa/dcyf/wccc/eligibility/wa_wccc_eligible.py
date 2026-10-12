from policyengine_us.model_api import *


class wa_wccc_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Washington Working Connections Child Care"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0005",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0023",
    )

    def formula(spm_unit, period, parameters):
        # RCW 43.216.802(7) bars considering the citizenship status of either
        # the applicant (parent) or the child, so no immigration check applies.
        has_eligible_child = add(spm_unit, period, ["wa_wccc_eligible_child"]) > 0
        income_eligible = spm_unit("wa_wccc_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("wa_wccc_activity_eligible", period)
        standard_path = income_eligible & asset_eligible
        # WAC 110-15-0023(2)(a): HGP families bypass the asset limit and
        # standard income tier. WAC 110-15-0023(2)(b) restricts HGP to
        # income strictly under 85% SMI (the smi_limit returns 85% SMI
        # when the household is homeless).
        is_hgp_eligible = spm_unit("wa_wccc_hgp_eligible", period)
        countable_income = spm_unit("wa_wccc_countable_income", period)
        income_limit = spm_unit("wa_wccc_smi_limit", period)
        hgp_path = is_hgp_eligible & (countable_income < income_limit)
        return has_eligible_child & activity_eligible & (standard_path | hgp_path)
