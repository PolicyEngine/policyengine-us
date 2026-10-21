from policyengine_us.model_api import *


class ny_pass_through_entity_tax_credit_claimed(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Claims a New York State or City pass-through entity tax credit"
    documentation = (
        "Whether the tax unit claims the New York State pass-through entity tax "
        "credit (Tax Law § 863(a)) or the New York City pass-through entity tax "
        "credit (Tax Law § 870(a)). PolicyEngine does not compute either credit."
    )
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/863",
        "https://www.nysenate.gov/legislation/laws/TAX/870",
        "https://www.tax.ny.gov/pdf/2025/inc/it270_2025_fill_in.pdf#page=1",
    )
    defined_for = StateCode.NY
    default_value = False
