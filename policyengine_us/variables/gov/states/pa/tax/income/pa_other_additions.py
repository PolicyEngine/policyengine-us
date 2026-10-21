from policyengine_us.model_api import *


class pa_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA
    documentation = (
        "Pennsylvania other additions to taxable income reported on "
        "Form PA-40, Line 8 (Other Income), entered as a positive amount."
    )
    reference = "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40in.pdf#page=13"
