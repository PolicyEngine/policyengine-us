from policyengine_us.model_api import *


class ar_taxable_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Arkansas taxable capital gains"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        lt_capital_gains = person("long_term_capital_gains", period)
        st_capital_gains = person("short_term_capital_gains", period)
        capital_loss = -st_capital_gains
        has_capital_loss = capital_loss > 0
        # Can be capital loss
        reduced_lt_capital_gain = where(
            has_capital_loss, lt_capital_gains - capital_loss, lt_capital_gains
        )
        p = parameters(
            period
        ).gov.states.ar.tax.income.gross_income.capital_gains
        capped_net_cap_gain = min_(reduced_lt_capital_gain, p.exempt.cap)
        taxable_capped_net_cap_gain = capped_net_cap_gain * (1 - p.exempt.rate)
        taxable_capital_gain = where(
            has_capital_loss,
            taxable_capped_net_cap_gain,
            st_capital_gains + taxable_capped_net_cap_gain,
        )

        taxable_capital_loss = -taxable_capital_gain
        has_taxable_capital_loss = taxable_capital_loss > 0
        # Taxable capital loss is capped separately
        filing_status = person.tax_unit("filing_status", period)
        loss_cap = p.loss_cap[filing_status]
        capped_capital_loss = min_(taxable_capital_loss, loss_cap)
        return where(
            has_taxable_capital_loss, capped_capital_loss, taxable_capital_gain
        )
