from policyengine_us.model_api import *


class form_4952_elected_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 elected investment income"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 4g: "Enter the amount from lines 4b and 4e that you elect
    to include in investment income." The instructions say "don't enter
    more than the sum of lines 4b and 4e". Sum the head's and spouse's
    investment_income_elected_form_4952, floor at zero, and cap at lines 4b
    plus 4e. A tax unit dependent's election belongs on the dependent's own
    Form 4952.

    The instructions also have filers enter this amount on "The Schedule D
    Tax Worksheet, line 3", so the capital gains tax uses this effective
    election. The line 4g note says the election is "attributable first to
    net capital gain" and "then to qualified dividends". No input exists for
    the alternative "Elec." allocation next to line 4e, so the default
    gain-first allocation applies.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_B_iii",
        "https://www.irs.gov/pub/irs-prior/f4952--2025.pdf#page=3",
    ]

    def formula(tax_unit, period, parameters):
        election = max_(
            0,
            tax_unit_non_dep_add(
                tax_unit, period, ["investment_income_elected_form_4952"]
            ),
        )
        qualified_dividends = tax_unit("form_4952_qualified_dividends", period)
        net_capital_gain = tax_unit("form_4952_net_capital_gain", period)
        return min_(election, qualified_dividends + net_capital_gain)
