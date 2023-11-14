from policyengine_us.model_api import *


class hi_state_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii state income tax addback"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=11"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=31" # State Tax Refund Worksheet
    )
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        # check eligible?
        # need go through Form N-11 – State Tax Refund Worksheet
        # only part b of Hawaii Additions Worksheet?
        # how to include values from 2021 n-11(the old one)
        p = parameters(period).gov.irs.deductions
        standard_deduction = tax_unit("standard_deduction", period)
        filing_status = tax_unit("filing_status", period)
        
        return 
