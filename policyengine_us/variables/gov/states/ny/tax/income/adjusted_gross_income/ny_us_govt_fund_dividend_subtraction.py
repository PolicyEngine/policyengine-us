from policyengine_us.model_api import *
from policyengine_us.tools.us_govt_obligation_funds import (
    us_govt_fund_state_subtraction,
)


class ny_us_govt_fund_dividend_subtraction(Variable):
    value_type = float
    entity = Person
    label = "New York subtraction for fund dividends from U.S. government obligations"
    documentation = (
        "Dividends from regulated investment companies attributable to "
        "interest on U.S. obligations, from each fund that met New York's "
        "asset test at the close of every quarter of its taxable year (Form "
        "IT-201 line 28, together with direct U.S. obligation interest from "
        "us_govt_interest)."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # N.Y. Tax Law § 612(c)(1)
        "https://newyork.public.law/laws/n.y._tax_law_section_612",
        # TSB-M-92(4)I
        "https://www.tax.ny.gov/pdf/memos/income/m92_4i.pdf",
        # Line 28
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=9",
    )
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.agi.subtractions.us_govt_fund_dividends
        return us_govt_fund_state_subtraction(person, period, p.asset_threshold)
