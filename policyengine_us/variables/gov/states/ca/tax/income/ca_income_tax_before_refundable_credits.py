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
        # Form 540 line 48: tax after nonrefundable credits
        itax = tax_unit("ca_income_tax_before_credits", period)
        nonrefundable_credits = tax_unit("ca_non_refundable_credits", period)
        tax_after_credits = max_(0, itax - nonrefundable_credits)
        # Form 540 lines 61-62: AMT and mental health services tax
        amt = tax_unit("ca_amt", period)
        mhst = tax_unit("ca_mental_health_services_tax", period)
        return tax_after_credits + amt + mhst
