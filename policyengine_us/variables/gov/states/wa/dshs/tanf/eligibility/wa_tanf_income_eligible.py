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
        # Get gross earned income from federal TANF variable
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Get maximum earned income limits by family size
        # Per WAC 388-478-0035, these limits "include the $500 family
        # earnings deduction" in their calculation
        p = parameters(period).gov.states.wa.dshs.tanf

        # Get household size, capped at maximum for which limits are defined
        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, p.maximum_family_size)

        # Gross earned income must be at or below the limit
        # Note: Unlike some states, WA tests GROSS income (not countable)
        # against published limits that already factor in the $500 disregard
        return gross_earned <= p.income.limit[size_capped]
