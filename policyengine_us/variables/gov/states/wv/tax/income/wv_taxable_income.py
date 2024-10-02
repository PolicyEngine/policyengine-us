from policyengine_us.model_api import *


class wv_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-4E/"
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        agi = tax_unit("wv_agi", period)
        low_income_exclusion = tax_unit(
            "wv_low_income_earned_income_exclusion", period
        )
        exemptions = tax_unit("wv_personal_exemption", period)
        return max_(agi - low_income_exclusion - exemptions, 0)
