from policyengine_us.model_api import *


class vt_percentage_capital_gains_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont percentage capital gains exclusion"
    unit = USD
    documentation = "This can be selected to be subtracted from federal adjusted gross income in Vermont as percentage capital gains exclusion."
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-153-2022.pdf#page=1"  # 2022 Schedule IN-153 Vermont Capital Gains Exclusion Calculation
        "https://legislature.vermont.gov/statutes/section/32/151/05811"  # Titl. 32 V.S.A. § 5811(21)(B)(ii)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-153%20Instr-2022.pdf"
    )

    def formula(tax_unit, period, parameters):
        # Get adjusted net capital gain, which is capped at 0
        adjusted_net_capital_gain = tax_unit(
            "adjusted_net_capital_gain", period
        )
        qualified_dividend_income = add(
            tax_unit, period, ["qualified_dividend_income"]
        )
        reduced_adjusted_net_capital_gain = max_(
            adjusted_net_capital_gain - qualified_dividend_income, 0
        )
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.exclusions.capital_gain
        # The percentage exclusion equals to a percentage of
        # the adjusted net capital gain and has a maximum value
        percentage_exclusion = (
            reduced_adjusted_net_capital_gain * p.percentage.rate
        )
        return min_(percentage_exclusion, p.percentage.cap)
