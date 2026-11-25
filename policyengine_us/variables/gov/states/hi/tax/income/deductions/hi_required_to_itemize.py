from policyengine_us.model_api import *


class hi_required_to_itemize(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Required to itemize deductions on the Hawaii resident return"
    documentation = (
        "The filer files a separate Hawaii return and their spouse itemizes "
        "on the Hawaii return, or files a return for a period of less than "
        "12 months because of a change in annual accounting period."
    )
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=15"
