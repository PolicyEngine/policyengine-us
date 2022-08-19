from openfisca_us.model_api import *


class pa_income_tax_forgiveness_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA income tax forgiveness rate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=21"
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        poverty_income = tax_unit("pa_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        filer_amount = parameters(period).gov.states.pa.tax.income.forgiveness.threshold.filer[filing_status]
        # Construct the full threshold by adding dependent amount.
        # Compute the associated rate by using np.floor or np.ceil.
