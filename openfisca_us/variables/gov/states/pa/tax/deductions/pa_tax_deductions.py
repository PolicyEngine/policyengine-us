from openfisca_us.model_api import *

# PA allows for four (4) deductions against income: Medical, Health, Tuition, and ABLE savings


class pa_tax_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA deductions against taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=20"
    defined_for = StateCode.PA
