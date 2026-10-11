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
        "to it."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l_5",
        "https://www.law.cornell.edu/uscode/text/26/1372",
        "https://www.irs.gov/pub/irs-prior/f7206--2023.pdf#page=1",
    )
    uprating = "calibration.gov.irs.soi.employment_income"
