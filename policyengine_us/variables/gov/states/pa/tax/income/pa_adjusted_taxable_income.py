from policyengine_us.model_api import *


class pa_adjusted_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA income tax after deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=21"
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("pa_total_taxable_income", period)
        deductions = tax_unit("pa_tax_deductions", period)
        return taxable_income - deductions
