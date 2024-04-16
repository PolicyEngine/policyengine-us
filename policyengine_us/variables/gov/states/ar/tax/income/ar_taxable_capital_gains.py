from policyengine_us.model_api import *


class ar_taxable_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Arkansas taxable capital gains"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        net_lt_capital_gains = person("long_term_capital_gains", period)
        net_st_capital_gains = person("short_term_capital_gains", period)
        # Can be capital loss
        net_cap_gain = net_lt_capital_gains - net_st_capital_gains
        p = parameters(
            period
        ).gov.states.ar.tax.income.gross_income.capital_gains
        capped_net_cap_gain = min_(net_cap_gain, p.exempt.cap)
        taxable_capped_net_cap_gain = capped_net_cap_gain * (1 - p.exempt.rate)
        st_capital_gain = max_(0, net_st_capital_gains)
        taxable_capital_gain = st_capital_gain + taxable_capped_net_cap_gain

        capital_loss = taxable_capital_gain < 0
        # Taxable capital loss is capped separately
        filing_status = person.tax_unit("filing_status", period)
        capped_capital_loss = max_(taxable_capital_gain, p.loss_cap[filing_status])
        return where(capital_loss, capped_capital_loss, taxable_capital_gain)
