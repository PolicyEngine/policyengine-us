from policyengine_us.model_api import *


class ga_surplus_tax_rebate(Variable):
    """
    Georgia surplus tax rebate - a one-time tax rebate for tax year 2022.
    
    This rebate was authorized under Georgia Code § 48-7-20.2 as part of the
    state's distribution of budget surplus funds to taxpayers. The rebate was
    issued only for tax year 2022 and varied by filing status:
    
    - Single/Separate filers: $250
    - Head of Household: $375
    - Joint/Surviving Spouse: $500
    
    The rebate amount is set to $0 for all years after 2022, reflecting its
    one-time nature. This rebate was automatically distributed to eligible
    taxpayers who filed a 2022 Georgia tax return.
    """
    value_type = float
    entity = TaxUnit
    label = "Georgia surplus tax rebate"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.legis.ga.gov/api/legislation/document/20232024/217823"
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.ga.tax.income.credits.surplus_tax_rebate
        # Returns the rebate amount based on filing status (non-zero only for 2022)
        return p.amount[filing_status]
