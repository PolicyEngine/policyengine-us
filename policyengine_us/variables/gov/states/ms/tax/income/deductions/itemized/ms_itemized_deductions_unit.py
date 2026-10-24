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
        # 2017 instructions, Form 80-108 lines 7a to 7d.
        "https://taxsim.nber.org/historical_state_tax_forms/MS/2017/80100178.pdf#page=15",
    )
    defined_for = StateCode.MS

    # itemized_deductions_less_salt already includes the federal miscellaneous
    # deduction above the 2% floor (Form 80-108 lines 7a to 7d before 2018).
    adds = [
        "itemized_deductions_less_salt",
        "ms_real_estate_tax_deduction",
    ]

    # Mississippi allows itemized deductions for gaming establishments and gender transition procedures
    # which are currently not modeled
