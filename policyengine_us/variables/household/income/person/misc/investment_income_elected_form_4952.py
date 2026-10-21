from policyengine_us.model_api import *


class investment_income_elected_form_4952(Variable):
    value_type = float
    entity = Person
    label = "investment income elected on Form 4952"
    documentation = (
        "Form 4952 line 4g: net capital gain and qualified dividends the "
        "taxpayer elects to include in investment income, which then lose "
        "the capital gains tax rates. Schedule D Tax Worksheet line 3."
    )
    unit = USD
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 163(d)(4)(B)",
            href="https://www.law.cornell.edu/uscode/text/26/163#d_4_B",
        ),
        dict(
            title="2025 Form 4952, line 4g",
            href="https://www.irs.gov/pub/irs-prior/f4952--2025.pdf",
        ),
    ]
