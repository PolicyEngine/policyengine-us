from policyengine_us.model_api import *
from policyengine_us.tools.us_govt_obligation_funds import (
    us_govt_fund_state_subtraction,
)


class ct_us_govt_fund_dividend_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Connecticut subtraction for exempt dividends from qualifying mutual funds"
    documentation = (
        "Exempt dividends from regulated investment companies derived from "
        "U.S. government obligations, from each fund that met Connecticut's "
        "asset test at the close of every quarter of its taxable year "
        "(Form CT-1040 line 40). Direct holdings of U.S. obligations go on "
        "line 39 through us_govt_interest."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # Conn. Gen. Stat. § 12-718
        "https://law.justia.com/codes/connecticut/title-12/chapter-229/section-12-718/",
        # Conn. Agencies Regs. § 12-701(a)(20)-3(a)(2)
        "https://regulations.justia.com/states/connecticut/title-12/subtitle-740-a/part-i/section-12-701-a-20-3/",
        # Line 40
        "https://portal.ct.gov/-/media/drs/forms/2025/income/2025-ct-1040-instructions_1225.pdf#page=8",
    )
    defined_for = StateCode.CT

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ct.tax.income.subtractions.us_govt_fund_dividends
        return us_govt_fund_state_subtraction(person, period, p.asset_threshold)
