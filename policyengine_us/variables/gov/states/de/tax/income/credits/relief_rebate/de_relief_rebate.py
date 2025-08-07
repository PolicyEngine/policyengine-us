from policyengine_us.model_api import *


class de_relief_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware relief rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://legis.delaware.gov/BillDetail?LegislationId=99311"
    defined_for = StateCode.DE

    # Assuming that each adult in Delaware has filed a 2020
    # income tax return
    def formula(tax_unit, period, parameters):
        head_spouse_count = tax_unit("head_spouse_count", period)
        p = parameters(period).gov.states.de.tax.income.credits.relief_rebate
        return head_spouse_count * p.amount
