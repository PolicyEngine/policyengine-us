from policyengine_us.model_api import *


class sc_net_capital_gain_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina net capital gain deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=15",
        "https://www.scstatehouse.gov/code/t12c006.php"
        # South Carolina Code of Laws Section 12-6-1150 (A)
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.sc.tax.income.deductions.net_capital_gain_deduction
        person = tax_unit.members
        capital_gains = person("capital_gains", period)
        #capital_gains = add(tax_unit, period ["capital_gains"])
        return max_(capital_gains * p.rate, 0)
