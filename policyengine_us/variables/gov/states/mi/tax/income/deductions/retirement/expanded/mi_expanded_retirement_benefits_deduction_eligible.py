from policyengine_us.model_api import *


class mi_expanded_retirement_benefits_deduction_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Michigan expanded retirement benefits deduction"
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (10)
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2023/2023-IIT-Forms/BOOK_MI-1040.pdf#page=20",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.expanded

        if p.availability:
            older_spouse_birth_year = tax_unit(
                "older_spouse_birth_year", period
            )
            return p.birth_year.calc(older_spouse_birth_year)
        else:
            return False
