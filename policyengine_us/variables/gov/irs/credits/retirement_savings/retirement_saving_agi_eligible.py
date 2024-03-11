from policyengine_us.model_api import *


class retirement_saving_agi_eligible(Variable):
    entity = TaxUnit
    definition_period = YEAR
    label = "Eligible person for the retirement saving contributions credit"
    value_type = bool
    reference = "https://www.irs.gov/pub/irs-pdf/f8880.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.retirement_saving
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        agi_threshold = p.threshold.agi[filing_status]

        return agi <= agi_threshold
