from policyengine_us.model_api import *


class az_property_tax_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona property tax credit income of the tax unit's members"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The income of the tax unit's members, dependents included, for the "
        "Arizona property tax credit (Form 140PTC Part 1 lines A to I). "
        "az_property_tax_credit_household_income adds it up over every tax "
        "unit in the household to give line J. It can be negative after a "
        "capital loss."
    )
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(H)(6)
        "https://www.law.cornell.edu/regulations/arizona/Ariz-Admin-Code-SS-R15-2C-502",
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=4",
    ]
    defined_for = StateCode.AZ

    adds = "gov.states.az.tax.income.credits.property_tax.income_sources"
