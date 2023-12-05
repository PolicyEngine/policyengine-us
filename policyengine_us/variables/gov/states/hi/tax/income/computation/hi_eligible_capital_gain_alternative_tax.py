from policyengine_us.model_api import *


class hi_eligible_capital_gain_alternative_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii alternative tax on eligible capital gain"
    unit = USD
    definition_period = YEAR
    defined_for = "hi_alternative_tax_on_capital_gains_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.alternative_tax
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("hi_taxable_income", period)  # line 1
        # line 4 of Hawaii Tax on Capital Gains Worksheet
        # on Hawaii Resident Income Tax Instructions N-11 Rev.2022, page=33
        net_lt_capital_gain = add(
            tax_unit, period, ["long_term_capital_gains"]
        )
        # line 7
        net_capital_gain = tax_unit("net_capital_gain", period)
        # line 8
        smaller_net_capital_gain = min_(net_capital_gain, net_lt_capital_gain)
        # Line 9 is including a reduction based on the net gain from the disposition of property held for investment, which is currently not modeled
        # Line 11
        reduced_taxable_income = taxable_income - smaller_net_capital_gain
        # Line 12
        cap = p.income_threshold[filing_status]
        # Line 13
        capped_reduced_income = max_(
            reduced_taxable_income,
            cap,
        )
        # net capital gains eligible for alternative tax, Line 14
        eligible_capital_gains = max_(
            0, taxable_income - capped_reduced_income
        )
        # line 15 alternative tax for eligible capital gains
        return eligible_capital_gains * p.rate
