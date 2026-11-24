from policyengine_us.model_api import *


class hi_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii deductions"
    unit = USD
    reference = (
        "https://data.capitol.hawaii.gov/sessions/session2026/bills/HB2329_CD1_.pdf#page=1",
        "https://files.hawaii.gov/tax/news/announce/ann26-06.pdf#page=2",
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=11",
        # PDF pages 15 (itemized deduction), 20 (standard deduction)
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15",
        # PDF pages 15, 20
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=15",
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("hi_itemizes", period)
        itemized = tax_unit("hi_itemized_deductions", period)
        standard = tax_unit("hi_standard_deduction", period)
        nonitemizer_charity = tax_unit("charitable_deduction_for_non_itemizers", period)
        tips = tax_unit("hi_tip_income_deduction", period)
        return where(itemizes, itemized, standard + nonitemizer_charity) + tips
