from policyengine_us.model_api import *


class wa_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington TANF income eligible"
    definition_period = MONTH
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-478-0035",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0170",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Get parameters
        p = parameters(
            period
        ).gov.states.wa.dshs.tanf.eligibility.income.gross_earned_income_limit

        # Get household size
        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, 10)

        # Get gross earned income limit for this family size
        income_limit = p[size_capped]

        # Get gross earned income
        gross_earned = spm_unit("wa_tanf_gross_earned_income", period)

        # Must be at or below the income limit
        return gross_earned <= income_limit
