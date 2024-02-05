from policyengine_us.model_api import *


class wv_low_income_family_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia low-income family tax credit"
    unit = USD
    reference = "https://code.wvlegislature.gov/11-21-22/"
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        alternative_minimum_tax = tax_unit("alternative_minimum_tax", period)
        return alternative_minimum_tax == 0
