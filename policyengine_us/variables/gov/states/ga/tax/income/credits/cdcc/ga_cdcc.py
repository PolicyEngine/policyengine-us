from policyengine_us.model_api import *


class ga_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia non-refundable dependent care credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        # Georgia matches the federal credit taken
        federal_cdcc = tax_unit("cdcc", period)
        rate = parameters(period).gov.states.ga.tax.income.credits.cdcc.rate
        return federal_cdcc * rate
