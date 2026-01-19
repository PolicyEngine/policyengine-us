from policyengine_us.model_api import *


class wa_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-478-0020",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0165",
    )
    defined_for = "wa_tanf_eligible"

    def formula(spm_unit, period, parameters):
        # Get payment standard based on assistance unit size
        # (capped at maximum_family_size, typically 10)
        payment_standard = spm_unit("wa_tanf_payment_standard", period)

        # Get countable income (after all disregards and deductions)
        countable_income = spm_unit("wa_tanf_countable_income", period)

        # Calculate benefit per WAC 388-450-0165:
        # "The department calculates the amount of your cash assistance
        # by subtracting your AU's countable income from the applicable
        # payment standard."
        return max_(payment_standard - countable_income, 0)
