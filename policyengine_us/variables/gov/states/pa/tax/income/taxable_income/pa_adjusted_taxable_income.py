from policyengine_us.model_api import *


class pa_adjusted_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA income tax after deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2021/2021_pa-40in.pdf#page=21"
    defined_for = StateCode.PA

    adds = ["pa_total_taxable_income"]
    subtracts = ["pa_tax_deductions"]
