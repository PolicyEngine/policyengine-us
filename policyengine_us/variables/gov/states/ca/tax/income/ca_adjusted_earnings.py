from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.adjusted_earnings import (
    earnings_before_zero_floor,
)


class ca_adjusted_earnings(Variable):
    value_type = float
    entity = Person
    label = "California personal earned income adjusted for self-employment tax"
    documentation = (
        "Earned income subject to California tax: California wages, which "
        "count the payroll HSA contributions that federal W-2 box 1 wages "
        "leave out, plus self-employment earnings, less the deductible part "
        "of self-employment tax, floored at zero."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.6",  # (d)(2)
        "https://www.ftb.ca.gov/forms/2025/2025-3506-instructions.html",  # Line 4
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",  # Line 1h
        "https://www.ftb.ca.gov/forms/2025/2025-1005-publication.pdf#page=10",
        "https://www.law.cornell.edu/cfr/text/26/1.21-2#b_3",
    )

    def formula(person, period, parameters):
        # R&TC 17052.6(d)(2) limits earned income to "earned income subject
        # to tax under this part", and FTB 3506 line 4 counts "other taxable
        # employee compensation". California does not exclude payroll HSA
        # contributions (Schedule CA (540) line 1h, column C), so its wages
        # (ca_taxable_wages, W-2 box 16) exceed federal taxable wages by them.
        taxable_wages = max_(
            person("ca_taxable_wages", period),
            person("irs_employment_income", period),
        )
        # FTB 3506 line 4 counts wages together with net earnings from
        # self-employment, so a business loss offsets the California wages
        # before the zero floor, as adjusted_earnings does for federal wages.
        return max_(
            0,
            earnings_before_zero_floor(person, period, parameters, taxable_wages),
        )
