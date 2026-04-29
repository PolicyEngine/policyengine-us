from policyengine_us.model_api import *


class wa_millionaires_tax_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Washington millionaires tax applies"
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=7"
    defined_for = StateCode.WA

    def formula(tax_unit, period, parameters):
        return parameters(period).gov.states.wa.tax.income.millionaires_tax.in_effect
