from policyengine_us.model_api import *


class ks_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "KS income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/k-4021.pdf"
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/k-4022.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    """
    def formula(tax_unit, period, parameters):
        itax = tax_unit("ks_income_tax_before_credits", period)
        nonrefundable_credits = tax_unit("ks_nonrefundable_credits", period)
        return max_(0, itax - nonrefundable_credits)
    """
