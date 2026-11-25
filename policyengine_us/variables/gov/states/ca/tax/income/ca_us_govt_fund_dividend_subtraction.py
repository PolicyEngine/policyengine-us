from policyengine_us.model_api import *
from policyengine_us.tools.us_govt_obligation_funds import (
    us_govt_fund_state_subtraction,
)


class ca_us_govt_fund_dividend_subtraction(Variable):
    value_type = float
    entity = Person
    label = "California subtraction for fund dividends from U.S. government obligations"
    documentation = (
        "Ordinary dividends from regulated investment companies that are "
        "attributable to interest on U.S. government obligations, from each "
        "fund that met California's asset test at the close of every quarter "
        "of its taxable year or is a qualified fund of funds. Direct holdings "
        "of U.S. obligations are subtracted through us_govt_interest."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # Cal. Rev. & Tax. Code § 17145(a), (b)(4), (c), (d)
        "https://law.justia.com/codes/california/code-rtc/division-2/part-10/chapter-3/article-3/section-17145/",
        # Schedule CA (540), Part I, Section A, line 2, column B
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.agi.us_govt_fund_dividends
        # California's asset base counts every obligation exempt from
        # California tax, including California municipal obligations; the
        # fund slots carry only U.S. government obligations, so a fund that
        # needs California municipal holdings to reach 50% must use the
        # issuer's statement as evidence.
        return us_govt_fund_state_subtraction(
            person,
            period,
            p.asset_threshold,
            p.qualified_fund_of_funds_exempt,
        )
