from policyengine_us.model_api import *


class ny_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York interest deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Interest for New York's itemized deduction: the federal "
        "interest_deduction with New York's pre-TCJA home mortgage interest "
        "in place of the federal home mortgage interest. Mortgage insurance "
        "premiums stay in it, and ny_itemized_deductions_max removes those "
        "New York disallows."
    )
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        "https://www.tax.ny.gov/pit/file/itemized-deductions-2025.htm#interest",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        # Starting from interest_deduction keeps an interest total supplied
        # directly (deductible_interest_expense); only the federal mortgage
        # component is swapped for New York's.
        federal_interest = tax_unit("interest_deduction", period)
        federal_mortgage_interest = add(
            tax_unit, period, ["deductible_mortgage_interest"]
        )
        ny_mortgage_interest = tax_unit("ny_mortgage_interest_deduction", period)
        return federal_interest - federal_mortgage_interest + ny_mortgage_interest
