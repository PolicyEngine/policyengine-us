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
        alternative_minimum_tax = tax_unit("alternative_minimum_tax", period)
        # Family size is the number of exemptions that may be legally claimed
        # (W. Va. Code 11-21-22A), so a return with zero exemptions, such as a
        # filer who can be claimed as a dependent, cannot claim the credit
        # (IT-140 instructions).
        has_exemption = tax_unit("exemptions_count", period) > 0
        return (alternative_minimum_tax == 0) & has_exemption
