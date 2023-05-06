from policyengine_us.model_api import *


class mi_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MI standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan standard deduction, only allowed for taxpayers born after 1946 who has reached the age of 67."
    reference = (
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["mi"].tax.income.deductions.standard
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)
        # Aged standard deduction.
        age_threshold = p.age
        aged_count = (tax_unit("age_head", period) >= age_threshold).astype(
            int
        )
        amount_per_aged = p.amount[filing_status]
        aged_deduction = aged_count * amount_per_aged
        return aged_deduction
