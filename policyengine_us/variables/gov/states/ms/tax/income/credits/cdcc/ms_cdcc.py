from policyengine_us.model_api import *


class ms_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi child and dependent care credit"
    unit = USD
    definition_period = YEAR
    defined_for = "ms_cdcc_eligible"
    reference = "https://legiscan.com/MS/text/HB1671/id/2767768"

    def formula(tax_unit, period, parameters):
        # Mississippi matches the federal credit taken
        cdcc = tax_unit("cdcc", period)
        p = parameters(period).gov.states.ms.tax.income.credits.cdcc
        return p.match * cdcc
