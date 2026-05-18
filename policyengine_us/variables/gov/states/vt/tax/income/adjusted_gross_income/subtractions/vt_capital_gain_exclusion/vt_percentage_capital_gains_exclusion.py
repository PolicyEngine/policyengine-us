from policyengine_us.model_api import *


class vt_percentage_capital_gains_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont percentage capital gains exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-153-2024.pdf#page=2",
        "https://legislature.vermont.gov/statutes/section/32/151/05811",
    )

    def formula(tax_unit, period, parameters):
        # Per VT Schedule IN-153: The 40% exclusion only applies to eligible assets.
        # Eligible assets exclude: stocks/bonds traded on exchanges, financial instruments,
        # depreciable personal property (except farm property/timber), and real estate.
        # Since standard capital gains inputs map to financial instruments (ineligible),
        # we only use explicitly designated VT-eligible capital gains.
        eligible_gains = add(
            tax_unit,
            period,
            ["long_term_capital_gains_on_assets_eligible_for_vt_exclusion"],
        )
        p = parameters(period).gov.states.vt.tax.income.agi.exclusions.capital_gain
        percentage_exclusion = eligible_gains * p.percentage.rate
        return min_(percentage_exclusion, p.percentage.cap)
