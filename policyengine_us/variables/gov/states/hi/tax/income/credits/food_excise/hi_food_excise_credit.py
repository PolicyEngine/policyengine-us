from policyengine_us.model_api import *


class hi_food_excise_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii Food/Excise Tax Credit"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=50",
        "https://files.hawaii.gov/tax/forms/2025/n311_i.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        # HRS 235-55.85(a): only a taxpayer who cannot be claimed as a
        # dependent may claim the credit, for each qualified exemption; the
        # exemption amount counts only filers who cannot be claimed when
        # either can. Minor children receiving public support count for this
        # credit under 235-55.85(c), so they keep their amount unless every
        # filer can be claimed.
        every_filer_dependent = tax_unit("every_filer_is_dependent_elsewhere", period)
        exemption_amount = tax_unit("hi_food_excise_exemption_amount", period)
        minor_child_amount = tax_unit(
            "hi_food_excise_credit_minor_child_amount", period
        )
        return exemption_amount + where(every_filer_dependent, 0, minor_child_amount)
