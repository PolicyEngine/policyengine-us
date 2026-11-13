from policyengine_us.model_api import *


class oh_modified_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio modified adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        # R.C. 5747.01(II): "Ohio adjusted gross income plus any amount
        # deducted under divisions (A)(28) and (34) of this section".
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=31",
        # 2024 Ohio IT 1040 instructions, MAGI worksheet
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2024/it1040-booklet.pdf#page=40",
    )
    defined_for = StateCode.OH

    adds = [
        "oh_agi",
        "oh_business_income_deduction",
        "oh_qualifying_capital_gain_deduction",
    ]
