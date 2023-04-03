from policyengine_us.model_api import *


class mn_elderly_disabled_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota elderly/disabled subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1r_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1r_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        mn_itax = parameters(period).gov.states.mn.tax.income
        p = mn_itax.subtractions.elderly_disabled
        filing_status = tax_unit("filing_status", period)

        agi_limit = p.agi_limit[filing_status]
        untaxed_oasdi_limit = p.untaxed_oasdi_limit[filing_status]
        
        # calculate the subtraction amount
        
        
        disablity_ben = add(tax_unit, period, ["social_security_disability"])
        untaxed_oasdi = (
            add(tax_unit, period, ["social_security"])
            - add(tax_unit, period, ["taxable_social_security"])
        )

