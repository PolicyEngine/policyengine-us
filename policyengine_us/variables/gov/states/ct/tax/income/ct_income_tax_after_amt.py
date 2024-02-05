from policyengine_us.model_api import *


class ct_income_tax_after_amt(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax after the addition of the alternative minimum tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/2022-CT-1040-Instructions_1222.pdf#page=2"  # line 10
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-1040_1222.pdf#page=1"  # line 10
    )

    adds = ["ct_amt", "ct_income_tax_after_personal_credits"]
