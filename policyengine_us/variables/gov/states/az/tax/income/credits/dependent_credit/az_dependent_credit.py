from policyengine_us.model_api import *


class az_dependent_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona dependent care credit"
    unit = USD
    documentation = "https://azdor.gov/file/12346/download?token=7FAdFbnT"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        amount = tax_unit("az_dependent_credit_amount", period)
        credit_rate = tax_unit("az_dependent_credit_rate", period)
        return amount * credit_rate
