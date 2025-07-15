from policyengine_us.model_api import *


class pa_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2022/2022_pa-40dc.pdf"  # 2022 form
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        # Get the federal CDCC value
        # Pennsylvania matches the potential federal credit
        cdcc = tax_unit("cdcc_potential", period)
        # Access the parameter path
        p = parameters(period).gov.states.pa.tax.income.credits.cdcc
        # Multiply the federal CDCC value by the Pennsylvania CDCC rate
        return p.match * cdcc
