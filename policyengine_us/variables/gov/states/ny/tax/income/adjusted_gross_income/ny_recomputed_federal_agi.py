from policyengine_us.model_api import *


class ny_recomputed_federal_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York recomputed federal adjusted gross income"
    unit = USD
    documentation = (
        "Federal adjusted gross income as reported, plus the Form IT-558 "
        "addition adjustments and less its subtraction adjustments (Form "
        "IT-201 line 19a). New York AGI, the credits and the itemized "
        "deduction floors and limitation start from it. The adjustment "
        "modeled is A-003: the 2020 federal charitable deduction for "
        "non-itemizers (IRC 62(a)(22)), which New York did not adopt."
    )
    definition_period = YEAR
    reference = (
        # 2020 IT-201 instructions, line 19a worksheet.
        "https://www.tax.ny.gov/pdf/2020/inc/it201i_2020.pdf#page=16",
        # 2020 IT-558 instructions, addition A-003.
        "https://www.tax.ny.gov/pdf/2020/inc/it558i_2020.pdf#page=2",
    )
    defined_for = StateCode.NY

    adds = ["adjusted_gross_income", "charitable_contributions_ald"]
