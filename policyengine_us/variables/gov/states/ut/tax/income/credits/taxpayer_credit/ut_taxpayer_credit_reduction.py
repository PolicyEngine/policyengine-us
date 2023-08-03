from policyengine_us.model_api import *


class ut_taxpayer_credit_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxpayer credit reduction"
    unit = USD
    documentation = "Form TC-40, line 19"
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        phase_out_income = tax_unit(
            "ut_taxpayer_credit_phase_out_income", period
        )
        phase_out_rate = parameters(
            period
        ).gov.states.ut.tax.income.credits.taxpayer.phase_out.rate
        return phase_out_income * phase_out_rate
