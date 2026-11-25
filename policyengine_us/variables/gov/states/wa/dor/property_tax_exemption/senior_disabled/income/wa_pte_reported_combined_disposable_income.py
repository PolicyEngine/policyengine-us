from policyengine_us.model_api import *


# Use a finite reserved value so an omitted report differs from zero or a loss.
UNREPORTED_COMBINED_DISPOSABLE_INCOME = -(2**100)


class wa_pte_reported_combined_disposable_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Reported Washington property tax combined disposable income for the preceding assessment year"
    definition_period = YEAR
    default_value = UNREPORTED_COMBINED_DISPOSABLE_INCOME
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/WAC/default.aspx?cite=458-16A-120",  # (3)
        "https://dor.wa.gov/sites/default/files/2022-02/64-0002.pdf#page=2",  # Part 5
    )
