from policyengine_us.model_api import *


class wa_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington TANF eligible"
    definition_period = MONTH
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=388-400-0005"
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        has_tanf_eligible_immigrant = (
            add(spm_unit, period, ["wa_tanf_immigration_status_eligible"]) > 0
        )
        show_all = spm_unit("wa_show_all_cash_assistance_programs", period)
        income_eligible = spm_unit("wa_tanf_income_eligible", period)
        resources_eligible = spm_unit("wa_tanf_resources_eligible", period.this_year)
        return (
            demographic_eligible
            & (has_tanf_eligible_immigrant | show_all)
            & income_eligible
            & resources_eligible
        )
