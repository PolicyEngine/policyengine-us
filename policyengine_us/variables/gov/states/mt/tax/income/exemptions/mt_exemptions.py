from policyengine_us.model_api import *


class mt_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        exemption_count = tax_unit("mt_exemptions_count", period)
        p = parameters(period).gov.states.mt.tax.income.exemptions
        return exemption_count * p.amount
