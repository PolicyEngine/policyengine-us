from policyengine_us.model_api import *


class ca_eitc_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "California earned income for the CalEITC, YCTC and FYTC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052",  # (c)(4)
        "https://www.ftb.ca.gov/forms/2023/2023-3514-instructions.html",  # Lines 13-19, Worksheet 3
        "https://www.ftb.ca.gov/forms/2025/2025-3514-booklet.html",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # FTB 3514 line 19 adds wages (line 16), nontaxable combat pay (line 17)
        # and business income or (loss) (line 18) for the whole return.
        # Worksheet 3 adds Schedule C income (Schedule 1 line 3), farm income
        # (Schedule 1 line 6) and partnership self-employment earnings (K-1
        # box 14, code A), and subtracts the deductible part of SE tax
        # (Schedule 1 line 15). A loss of one spouse therefore offsets the
        # other spouse's wages before the result is floored at zero. R&TC
        # 17052(c)(4) applies IRC 32(c)(2)(A), which the federal EITC earned
        # income computes from these same sources.
        return tax_unit("eitc_earned_income", period)
