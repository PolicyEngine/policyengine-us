from policyengine_us.model_api import *


class mi_wagering_losses_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan wagering losses deduction"
    unit = USD
    documentation = (
        "Michigan subtraction, from 2021, for the wagering losses a casual "
        "gambler deducts as an itemized deduction on the federal return."
    )
    definition_period = YEAR
    reference = (
        # 2021 PA 168, MCL 206.30
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-30",
        "https://www.michigan.gov/taxes/rep-legal/notices/notice-new-tax-treatment-of-wagering-losses-for-casual-gamblers-under-the-michigan-income-tax-act",
        # 2025 MI-1040 booklet, Schedule 1 line 23
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=16",
        # 2025 Taxpayer Assistance Manual: the federal 90% limit carries over
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Tax-Professional/2025-Taxpayer-Assistance-Manual.pdf#page=99",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        # Only the losses claimed as an itemized deduction on the federal
        # return count, so a filer who takes the federal standard deduction
        # has none.
        itemizes = tax_unit("tax_unit_itemizes", period)
        return itemizes * tax_unit("wagering_losses_deduction", period)
