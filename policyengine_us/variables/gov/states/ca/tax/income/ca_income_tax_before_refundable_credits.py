from policyengine_us.model_api import *


class ca_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA income tax before refundable credits"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/Search/Home/Confirmation"

    def formula(tax_unit, period, parameters):
        itax = tax_unit("ca_income_tax_before_credits", period)
        nonrefundable_credits = tax_unit("ca_nonrefundable_credits", period)
        return max_(0, itax - nonrefundable_credits)
