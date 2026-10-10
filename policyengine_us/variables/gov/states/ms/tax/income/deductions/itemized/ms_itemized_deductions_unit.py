from policyengine_us.model_api import *


class ms_itemized_deductions_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi itemized deductions"
    unit = USD
    definition_period = YEAR

    reference = (
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100221.pdf#page=15",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80108228.pdf",  # Line 7
        "https://law.justia.com/codes/mississippi/title-27/chapter-7/article-1/section-27-7-17/",
        # 2025 instructions: Schedule A line 7b (gaming losses), and the 3%
        # tax on winnings reported by Mississippi casinos
        # PDF pages 16, 25
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=16",
    )
    defined_for = StateCode.MS

    adds = [
        "itemized_deductions_less_salt",
        "misc_deduction",
        "ms_real_estate_tax_deduction",
    ]
    # Winnings reported by Mississippi casinos bear a separate 3% tax and are
    # not Mississippi income, and Mississippi gaming losses come off the
    # itemized deductions (Schedule A line 7b). Mississippi income here
    # leaves out all gambling winnings, including those from other states,
    # so the federal wagering losses deduction is left out as well.
    subtracts = ["wagering_losses_deduction"]

    # Mississippi allows itemized deductions for gaming establishments and gender transition procedures
    # which are currently not modeled
