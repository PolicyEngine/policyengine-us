from policyengine_us.model_api import *


class sc_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/forms-site/Forms/TC60_2021.pdf"

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        rate = parameters(period).gov.states.sc.tax.income.credits.eitc.rate
        return np.round(federal_eitc * rate, 1)
