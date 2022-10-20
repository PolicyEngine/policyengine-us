from policyengine_us.model_api import *


class pa_total_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA total taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=8"
    defined_for = StateCode.PA

    formula = sum_of_variables(["adjusted_gross_income"])
