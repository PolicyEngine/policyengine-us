from policyengine_us.model_api import *


class niit_magi_section_911_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "Section 911 addition to modified adjusted gross income for the net investment income tax"
    unit = USD
    documentation = (
        "The amount 26 U.S.C. 1411(d) adds to adjusted gross income: the "
        "foreign earned income excluded under section 911(a)(1), less the "
        "deductions and exclusions disallowed under section 911(d)(6) for it. "
        "On the Form 8960 Line 13 MAGI Worksheet this is line 2c: Form 2555 "
        "line 42 less the Form 2555 line 44 deductions allocable to it. "
        "Section 1411(d) does not add back the housing exclusion of section "
        "911(a)(2) (Form 2555 line 36) or the housing deduction (line 50). "
        "The default is foreign_earned_income_exclusion, which holds the "
        "housing amounts as well (Form 2555 lines 45 and 50), so for a filer "
        "with a housing exclusion or deduction the default overstates MAGI by "
        "the net housing amount. For such a filer, enter the worksheet amount "
        "directly."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1411#d",
        "https://www.law.cornell.edu/uscode/text/26/911#a",
        "https://www.law.cornell.edu/cfr/text/26/1.1411-2",
        "https://www.irs.gov/pub/irs-prior/i8960--2025.pdf#page=22",
        "https://www.irs.gov/pub/irs-prior/i8960--2025.pdf#page=23",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
    )

    def formula(tax_unit, period, parameters):
        return max_(0, tax_unit("foreign_earned_income_exclusion", period))
