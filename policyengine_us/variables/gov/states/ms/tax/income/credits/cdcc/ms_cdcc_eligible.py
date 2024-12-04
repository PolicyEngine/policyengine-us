from policyengine_us.model_api import *


class ms_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Mississippi child and dependent care credit"
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = "https://legiscan.com/MS/text/HB1671/id/2767768"

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states.ms.tax.income.credits.cdcc
        return agi <= p.income_limit
