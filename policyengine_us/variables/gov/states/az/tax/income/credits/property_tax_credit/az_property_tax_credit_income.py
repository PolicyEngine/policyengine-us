from policyengine_us.model_api import *


class az_property_tax_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income for the Arizona property tax credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Household income for the Arizona property tax credit, Form 140PTC Part 1 "
        "line J. It can be negative after a capital loss; the credit schedules "
        "then use zero."
    )
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(H)(6)
        "https://www.law.cornell.edu/regulations/arizona/Ariz-Admin-Code-SS-R15-2C-502",
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=4",
    ]
    defined_for = StateCode.AZ

    adds = "gov.states.az.tax.income.credits.property_tax.income_sources"
