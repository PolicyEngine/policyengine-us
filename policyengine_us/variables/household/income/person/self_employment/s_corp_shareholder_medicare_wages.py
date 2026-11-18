from policyengine_us.model_api import *


class s_corp_shareholder_medicare_wages(Variable):
    value_type = float
    entity = Person
    label = "S corporation shareholder Medicare wages"
    unit = USD
    documentation = (
        "Medicare wages (Form W-2 box 5) from an S corporation in which the "
        "person is a more-than-2% shareholder (section 1372(b)). Section "
        "162(l)(5) treats these wages as the shareholder's earned income for "
        "the self-employed health insurance deduction (Form 7206 line 11). "
        "Like the other income inputs, enter the amount left after any "
        "section 911 foreign earned income exclusion attributable to these "
        "wages (line 12). They are part of employment_income, not in addition "
        "to it. Premiums the corporation pays or reimburses for the "
        "shareholder and reports in box 1 as wages count as the "
        "shareholder's own: include them in employment_income and in "
        "health_insurance_premiums, but not here, because box 5 leaves out "
        "premiums paid under a plan for employees generally (section "
        "3121(a)(2)(B)). The model has no wage input that is in box 1 but "
        "not box 5, so those premiums also count as payroll tax wages. "
        "Long-term care premiums the corporation pays or reimburses and "
        "reports in box 1 go in employment_income and in "
        "long_term_health_insurance_premiums, on the insured person. "
        "The model's payroll tax wages start from employment_income, so it "
        "taxes these premiums as payroll wages too. The deduction "
        "counts both premium inputs only when "
        "is_self_employed is true, so set it for a shareholder even when "
        "these wages are their only earned income."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l_5",
        "https://www.law.cornell.edu/uscode/text/26/1372",
        "https://www.law.cornell.edu/uscode/text/26/3121#a_2",
        "https://www.irs.gov/pub/irs-prior/f7206--2023.pdf#page=1",
        # Notice 2008-1: premiums are box 1 wages but not Social Security
        # or Medicare wages when section 3121(a)(2)(B) applies
        "https://www.irs.gov/pub/irs-drop/n-08-01.pdf#page=2",
    )
    uprating = "calibration.gov.irs.soi.employment_income"
