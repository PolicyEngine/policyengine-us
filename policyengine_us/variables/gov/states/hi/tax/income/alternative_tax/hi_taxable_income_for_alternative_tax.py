from policyengine_us.model_api import *


class hi_taxable_income_for_alternative_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Hawaii eligible capital gains for the alternative tax capital gains"
    )
    unit = USD
    definition_period = YEAR
    defined_for = "hi_alternative_tax_on_capital_gains_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income
        filing_status = tax_unit("filing_status", period)
        # line 1 of Hawaii Tax on Capital Gains Worksheet
        # on Hawaii Resident Income Tax Instructions N-11 Rev.2022, page=33
        taxable_income = tax_unit("hi_taxable_income", period)
        # line 4
        net_lt_capital_gain = add(
            tax_unit, period, ["long_term_capital_gains"]
        )
        # line 7
        net_capital_gain = tax_unit("net_capital_gain", period)
        # line 8
        smaller_net_capital_gain = min_(net_capital_gain, net_lt_capital_gain)
        # The filer is eligible to compute the tax on the smaller of the taxable income less capital gains
        # or the taxable income capped at a threshold below the tax on capital gains rate
        reduced_taxable_income = taxable_income - smaller_net_capital_gain
        cap_single = p.rates.single.thresholds[6]
        cap_joint = p.rates.joint.thresholds[6]
        cap_widow = p.rates.widow.thresholds[6]
        cap_separate = p.rates.separate.thresholds[6]
        cap_hoh = p.rates.head_of_household.thresholds[6]
        statuses = filing_status.possible_values
        cap = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.JOINT,
                filing_status == statuses.WIDOW,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                cap_single,
                cap_joint,
                cap_widow,
                cap_separate,
                cap_hoh,
            ],
        )
        capped_taxable_income = min_(taxable_income, cap)
        return max_(reduced_taxable_income, capped_taxable_income)
