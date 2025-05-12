from policyengine_us.model_api import *


class taxable_income_deductions_if_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Deductions if itemizing"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/63"
    definition_period = YEAR

    adds = [
        "itemized_taxable_income_deductions",
        "qualified_business_income_deduction",
        "wagering_losses_deduction",
    ]
