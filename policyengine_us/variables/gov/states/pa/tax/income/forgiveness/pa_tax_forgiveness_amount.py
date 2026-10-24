from policyengine_us.model_api import *


class pa_tax_forgiveness_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA forgiveness amount"
    unit = USD
    definition_period = YEAR
    reference = "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2021/2021_pa-40in.pdf#page=21"
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        income_tax = tax_unit("pa_income_tax_before_forgiveness", period)
        rate = tax_unit("pa_tax_forgiveness_rate", period)
        # Forgiveness applies only to the tax of a filer who can claim it.
        eligible_share = tax_unit("pa_tax_forgiveness_eligible_share", period)
        return income_tax * rate * eligible_share
