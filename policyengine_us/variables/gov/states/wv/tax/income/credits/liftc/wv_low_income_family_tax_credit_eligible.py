from policyengine_us.model_api import *


class wv_low_income_family_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia low-income family tax credit"
    unit = USD
    reference = (
        "https://code.wvlegislature.gov/11-21-22/",
        "https://code.wvlegislature.gov/11-21-22A/",
        "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=13",
    )
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        # W. Va. Code 11-21-22A(e) sets no minimum number of exemptions, and
        # family size counts the 11-21-16(d) exemption of a filer who can be
        # claimed as a dependent, so every return has a family size of one or
        # more.
        alternative_minimum_tax = tax_unit("alternative_minimum_tax", period)
        return alternative_minimum_tax == 0
