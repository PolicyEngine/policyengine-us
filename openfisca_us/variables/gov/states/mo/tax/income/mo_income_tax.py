from openfisca_us.model_api import *


class mo_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO income tax"
    unit = USD
    documentation = "Missouri State income tax."
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-1040%20Print%20Only_2021.pdf"

    def formula(tax_unit, period, parameters):
        in_mo = tax_unit.household("state_code_str", period) == "MO"

        income_tax_before_credits = tax_unit(
            "mo_income_tax_before_credits", period
        )

        # CREDITS =  [
        #     # "mo_resident_credit",  # this seems to relate to paying taxes in other states
        #     # "mo_misc_tax_credits",  # sum of credits found here - https://dor.mo.gov/forms/MO-TC_2021.pdf
        #     # "mo_property_tax_credit",
        # ]

        # credit_value = add(tax_unit, period, CREDITS)
        credit_value = 0
        return in_mo * (income_tax_before_credits - credit_value)
