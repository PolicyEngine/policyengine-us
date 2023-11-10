from policyengine_us.model_api import *


class mt_social_security_benefit_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana taxable social security benefit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf"
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        exceeding_income = tax_unit("mt_social_security_benefit_exceeding_income", period)
        return exceeding_income >= 0