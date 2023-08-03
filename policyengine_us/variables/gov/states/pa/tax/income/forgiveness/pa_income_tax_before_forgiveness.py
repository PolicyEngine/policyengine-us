from policyengine_us.model_api import *


class pa_income_tax_before_forgiveness(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA income tax before forgiveness"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=21"
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("pa_adjusted_taxable_income", period)
        rate = parameters(period).gov.states.pa.tax.income.rate
        return taxable_income * rate
