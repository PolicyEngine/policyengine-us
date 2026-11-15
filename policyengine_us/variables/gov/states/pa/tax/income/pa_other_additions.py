from policyengine_us.model_api import *


class pa_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA
    documentation = (
        "Enter a positive amount for other income taxable in Pennsylvania under "
        "one of the eight classes (lines 1c-8, total on line 9) that PolicyEngine "
        "does not otherwise include, excluding gambling winnings, which "
        "PolicyEngine already includes."
    )
    # PDF pages 8, 19-20
    reference = "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40in.pdf#page=8"
