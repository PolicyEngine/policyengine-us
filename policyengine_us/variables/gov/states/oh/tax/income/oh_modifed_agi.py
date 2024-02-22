from policyengine_us.model_api import *


class oh_modified_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio modified adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.71",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=31",
    )
    defined_for = StateCode.OH

    adds = ["oh_agi", "qualified_business_income_deduction"]
