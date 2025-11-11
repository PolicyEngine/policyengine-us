from policyengine_us.model_api import *


class wa_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington TANF eligible"
    definition_period = MONTH
    reference = ("https://app.leg.wa.gov/wac/default.aspx?cite=388-400-0005",)
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Check resource eligibility
        resources_eligible = spm_unit(
            "wa_tanf_resources_eligible", period.this_year
        )

        # Check income eligibility
        income_eligible = spm_unit("wa_tanf_income_eligible", period)

        # Overall eligibility requires both resource and income eligibility
        return resources_eligible & income_eligible
