from policyengine_us.model_api import *


class vt_percentage_capital_gains_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont percentage capital gains exclusion"
    unit = USD
    documentation = (
        "Up to 40% of net capital gains from eligible assets held "
        "3+ years, capped at $350,000. Only applies to qualifying "
        "assets (excludes publicly traded stocks/bonds, financial "
        "instruments, depreciable personal property except farm "
        "property/timber, and residential real estate). Defaults to "
        "0 since PolicyEngine cannot distinguish asset types."
    )
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-153-2024.pdf#page=2",
        "https://legislature.vermont.gov/statutes/section/32/151/05811",
    )

    def formula(tax_unit, period, parameters):
        eligible_gains = tax_unit(
            "vt_capital_gains_from_eligible_assets", period
        )
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.exclusions.capital_gain
        percentage_exclusion = eligible_gains * p.percentage.rate
        return min_(percentage_exclusion, p.percentage.cap)
