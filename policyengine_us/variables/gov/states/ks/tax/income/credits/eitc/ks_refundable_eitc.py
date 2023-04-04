from policyengine_us.model_api import *


class ks_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas refundable EITC amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        total_eitc = tax_unit("ks_total_eitc", period)
        nonrefundable_eitc = tax_unit("ks_nonrefundable_eitc", period)
        return max_(0, total_eitc - nonrefundable_eitc)
