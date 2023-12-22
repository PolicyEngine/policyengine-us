from policyengine_us.model_api import *


class hi_tax_on_capped_reduced_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii tax on capped reduced capital gains (not eligible for alternative tax)"
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
        eligible_capital_gains = max_(
            0, taxable_income - capped_reduced_income
        )  # net capital gains eligible for alternative tax, Line 14
        # tax --- line 15
        statuses = filing_status.possible_values
        rate_p = parameters(period).gov.states.hi.tax.income.rates
        return select(
            [
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.WIDOW,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                rate_p.separate.calc(capped_reduced_income),
                rate_p.joint.calc(capped_reduced_income),
                rate_p.widow.calc(capped_reduced_income),
                rate_p.head_of_household.calc(capped_reduced_income),
            ],
            default=rate_p.single.calc(capped_reduced_income),
        )
