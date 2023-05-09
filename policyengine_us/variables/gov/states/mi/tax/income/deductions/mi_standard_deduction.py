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
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf?rev=86a928564e3f42449c531309673f5da7&hash=7147C48E7C9B1B8171B72DC34A66642A",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["mi"].tax.income.deductions.standard
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)
        # Aged standard deduction.
        age_min_threshold = p.min_age
        age_max_threshold = p.max_age
        aged_head = (
            tax_unit("age_head", period) >= age_min_threshold
            and tax_unit("age_head", period) <= age_max_threshold
        ).astype(int)
        aged_spouse = (
            tax_unit("age_spouse", period) >= age_min_threshold
            and tax_unit("age_head", period) <= age_max_threshold
        ).astype(int)
        aged_count = max_(aged_head, aged_spouse)
        amount_per_aged = p.amount[filing_status]
        aged_deduction = aged_count * amount_per_aged
        return aged_deduction
