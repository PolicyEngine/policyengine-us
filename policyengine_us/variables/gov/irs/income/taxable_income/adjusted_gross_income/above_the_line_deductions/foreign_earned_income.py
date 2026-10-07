from policyengine_us.model_api import *


class foreign_earned_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Foreign earned income exclusion"
    unit = USD
    documentation = "Income earned and any housing expense in foreign countries that is excluded from adjusted gross income under 26 U.S. Code § 911. Other income inputs are the amounts left after the exclusion. Section 911(f) adds this amount back to set the tax rates on that income: line 2c of the Foreign Earned Income Tax Worksheet (Form 2555 lines 45 and 50, less deductions disallowed because they relate to the excluded income). The net investment income tax adds back only the section 911(a)(1) part; see niit_magi_section_911_addition."
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/911",
        "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=37",
    ]
