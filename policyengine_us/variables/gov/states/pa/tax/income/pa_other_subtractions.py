from policyengine_us.model_api import *


class pa_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA
    documentation = (
        "Pennsylvania other deductions against taxable income reported on "
        "Form PA-40, Line 11 (Deductions), entered as a positive amount, "
        "excluding items PolicyEngine calculates separately."
    )
    reference = "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40in.pdf#page=14"
