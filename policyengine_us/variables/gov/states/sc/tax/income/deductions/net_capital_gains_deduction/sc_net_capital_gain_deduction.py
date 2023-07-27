from policyengine_us.model_api import *


class sc_net_capital_gains_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina net capital gains deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=15"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.sc.tax.income.deductions.net_capital_gains_deduction
        ltcg = add(tax_unit, period, ["long_term_capital_gains"])
        ltcl = add(tax_unit, period, ["long_term_capital_losses"])
        stcl = add(tax_unit, period, ["short_term_capital_losses"])

        # SC Net Captial Gain = (ltcg-ltcl)-stcl
        sc_net_long_term_capital_gains = max_(ltcg - ltcl, 0)
        sc_net_capital_gains = max_(sc_net_long_term_capital_gains - stcl, 0)

        return sc_net_capital_gains * p.rate
