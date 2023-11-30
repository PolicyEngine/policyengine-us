from policyengine_us.model_api import *


class mt_social_security_benefits_exceeding_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana taxable social security benefits exceeding income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2110/",
        "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf#page=6",
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=6",
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.mt.tax.income.adjustments.social_security
        modified_income_cap = p.income_threshold[filing_status]
        modified_income = tax_unit("mt_modified_income", period)
        return max_(0, modified_income - modified_income_cap)
