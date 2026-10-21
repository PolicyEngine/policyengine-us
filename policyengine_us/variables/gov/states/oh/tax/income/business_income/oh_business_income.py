from policyengine_us.model_api import *


class oh_business_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio business income"
    documentation = "Ohio Schedule of Business Income, line 10."
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2024/1040-bundle-original-fi.pdf#page=5",
    )
    defined_for = StateCode.OH

    adds = ["oh_business_income_person"]
