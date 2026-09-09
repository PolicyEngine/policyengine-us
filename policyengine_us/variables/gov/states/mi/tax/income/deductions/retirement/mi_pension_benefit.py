from policyengine_us.model_api import *


class mi_pension_benefit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan pension benefit"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan retirement and pension benefits of qualifying age."
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        tier_one = tax_unit("mi_retirement_benefits_deduction_tier_one", period)
        tier_three = tax_unit("mi_retirement_benefits_deduction_tier_three", period)
        expanded = tax_unit("mi_expanded_retirement_benefits_deduction", period)
        standard_deduction = tax_unit("mi_standard_deduction", period)

        # Taxpayers who claim the expanded deduction via the standard deduction
        # (e.g. Tier 2 filers) do not double-claim it as a pension benefit.
        expanded_pension = where(standard_deduction >= expanded, 0, expanded)
        return max_(tier_one + tier_three, expanded_pension)
