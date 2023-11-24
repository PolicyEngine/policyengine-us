from policyengine_us.model_api import *


class mt_social_security_benefits_exceeding_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana taxable social security benefits exceeding income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf"
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.mt.tax.income.adjustments.social_security
        modified_income_cap = p.modified_income_cap[filing_status]
        modified_income = tax_unit("mt_modified_income", period)
        return max_(0, modified_income - modified_income_cap)
