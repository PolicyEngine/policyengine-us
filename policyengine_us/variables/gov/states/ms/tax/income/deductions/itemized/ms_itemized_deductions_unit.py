from policyengine_us.model_api import *


class ms_itemized_deductions_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi itemized deductions"
    unit = USD
    definition_period = YEAR

    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf",  # Line 7
        "https://law.justia.com/codes/mississippi/title-27/chapter-7/article-1/section-27-7-17/",
    )
    defined_for = StateCode.MS

    adds = [
        "itemized_deductions_less_salt",
        "misc_deduction",
        "ms_real_estate_tax_deduction",
    ]

    # Mississippi allows itemized deductions for gaming establishments and gender transition procedures
    # which are currently not modeled
