from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.filer_schedule_d_lines import (
    filer_schedule_d_lines,
)


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
        # 32 V.S.A. 5811(21)(B)(ii) excludes 40% of gains on "assets held by
        # the taxpayer for more than three years", to the extent included in
        # federal adjusted gross income. A tax unit dependent's gains are on
        # the dependent's own return, so only the head's and spouse's count.
        eligible_gains = tax_unit_non_dep_add(
            tax_unit,
            period,
            ["long_term_capital_gains_on_assets_eligible_for_vt_exclusion"],
        )
        # Schedule IN-153 line 15: eligible gains after netting, so no more
        # than Part I line 4, the smaller of the filers' Schedule D lines 15
        # and 16 less lines 18 and 19. Line 4 comes before the Form 4952
        # election, which IN-153 allocates separately (lines 5-7 and 16).
        lines = filer_schedule_d_lines(tax_unit, period)
        net_gain = min_(lines.line_15, lines.line_16) - (
            tax_unit("capital_gains_28_percent_rate_gain", period)
            + tax_unit("schedule_d_unrecaptured_section_1250_gain", period)
        )
        eligible_gains = max_(0, min_(eligible_gains, net_gain))
        # Lines 5-7 and 16: the share of the filers' Form 4952 election that
        # falls on net capital gain, line 4g x line 4e / (line 4b + line 4e),
        # taking line 4e as the filers' net capital gain and line 4b as their
        # qualified dividends. Line 16 uses this share when no investment
        # interest is for ineligible assets.
        election = max_(
            0,
            tax_unit_non_dep_add(
                tax_unit, period, ["investment_income_elected_form_4952"]
            ),
        )
        net_capital_gain = max_(0, min_(lines.line_15, lines.line_16))
        qualified_dividends = max_(
            0, tax_unit_non_dep_add(tax_unit, period, ["qualified_dividend_income"])
        )
        denominator = qualified_dividends + net_capital_gain
        election_on_gain = np.divide(
            election * net_capital_gain,
            denominator,
            out=np.zeros_like(denominator),
            where=denominator > 0,
        )
        eligible_gains = max_(0, eligible_gains - election_on_gain)
        p = parameters(period).gov.states.vt.tax.income.agi.exclusions.capital_gain
        percentage_exclusion = eligible_gains * p.percentage.rate
        return min_(percentage_exclusion, p.percentage.cap)
