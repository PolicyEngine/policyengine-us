from policyengine_us.model_api import *


class ct_social_security_benefit_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Connecticut social security benefit adjustment"
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.subtractions.social_security
        filing_status = tax_unit("filing_status", period)
        ss_benefit = add(tax_unit, period, ["social_security_benefits"])
        max_amount = p.amount[filing_status]
        return ss_benefit if ss_benefit > max_amount else 0      
