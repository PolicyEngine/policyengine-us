from policyengine_us.model_api import *


class sc_net_capital_gains_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina net capital gains deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=15",
        https://www.scstatehouse.gov/code/t12c006.php
        # South Carolina Code of Laws Section 12-6-1150 (A)
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.sc.tax.income.deductions.net_capital_gains_deduction
        sc_net_long_term_capital_gains = max_(
            0, add(tax_unit, period, ["long_term_capital_gains"])
        )
        sc_net_short_term_capital_gains = add(
            tax_unit, period, ["short_term_capital_gains"]
        )

        sc_net_capital_gains = max_(
            0, sc_net_long_term_capital_gains + sc_net_short_term_capital_gains
        )
        return sc_net_capital_gains * p.rate
