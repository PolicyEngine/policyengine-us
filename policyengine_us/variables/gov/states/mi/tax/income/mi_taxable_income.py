from policyengine_us.model_api import *


class mi_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/Schedule-1.pdf",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040.pdf",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        # Michigan computes taxable income from federal AGI, additions, subtractions,
        # and exemptions
        agi = tax_unit("adjusted_gross_income", period)
        additions = tax_unit("mi_additions", period)
        subtractions = tax_unit("mi_subtractions", period)
        exemptions = tax_unit("mi_exemptions", period)

        return max_(agi + additions - subtractions - exemptions, 0)
