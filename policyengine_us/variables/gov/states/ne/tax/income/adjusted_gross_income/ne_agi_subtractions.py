from policyengine_us.model_api import *


class ne_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska subtractions from federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
        "https://revenue.nebraska.gov/about/2023-nebraska-legislative-changes"
        "https://www.nebraskalegislature.gov/FloorDocs/108/PDF/Slip/LB754.pdf#page=10"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.agi.subtractions
        total_subtractions = add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
