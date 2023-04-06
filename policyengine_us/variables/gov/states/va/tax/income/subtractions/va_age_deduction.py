from policyengine_us.model_api import *


class va_age_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia age deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=16"
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions
        filing_status = tax_unit("filing_status", period)
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        age_deduction_amount = 0  # in progress
        eligible_count = sum(where(age_head>64, 1, 0) + where(age_spouse>64, 1, 0))

        return age_deduction_amount
