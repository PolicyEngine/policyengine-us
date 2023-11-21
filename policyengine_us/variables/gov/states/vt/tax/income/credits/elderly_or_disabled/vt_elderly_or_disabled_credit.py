from policyengine_us.model_api import *


class vt_elderly_or_disabled_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont Elderly or disabled credit"
    documentation = "Schedule R credit for the elderly and the disabled"
    unit = USD
    reference = (
        "https://tax.vermont.gov/individuals/personal-income-tax/tax-credits"
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.vt.tax.income.credits.elderly_or_disabled
        return p.match * tax_unit("elderly_disabled_credit", period)
