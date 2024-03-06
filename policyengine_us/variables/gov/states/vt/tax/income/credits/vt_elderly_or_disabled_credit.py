from policyengine_us.model_api import *


class vt_elderly_or_disabled_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont elderly or disabled credit"
    documentation = "Schedule R credit for the elderly and the disabled"
    unit = USD
    reference = (
        "https://tax.vermont.gov/individuals/personal-income-tax/tax-credits"
    )
    defined_for = StateCode.VT
    # The Investment Tax Credit and Vermont Farm Income Averaging Credit are also subject to the match
    # these are currently not included

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits
        us_elderly_disabled_credit = tax_unit(
            "elderly_disabled_credit", period
        )
        return p.elderly_or_disabled * us_elderly_disabled_credit
