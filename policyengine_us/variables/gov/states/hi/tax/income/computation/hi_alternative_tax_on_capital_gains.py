from policyengine_us.model_api import *


class hi_alternative_tax_on_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii alternative tax on capital gains"
    unit = USD
    definition_period = YEAR
    defined_for = "hi_alternative_tax_on_capital_gains_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.hi.tax.income.alternative_tax
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("hi_taxable_income", period)
        net_lt_capital_gain = add(person, period, ["long_term_capital_gains"])
        net_capital_gain = tax_unit("net_capital_gain", period)
        # line_9
        cap = p.max_amount[filing_status]
        eligibility = tax_unit(
            "hi_alternative_tax_on_capital_gains_eligible", period
        ).astype(int)

        # line 13
        ineligible_income = max_(
            taxable_income
            - min_(net_capital_gain, net_lt_capital_gain),  # line 11
            cap,
        )

        # line 14
        eligible_income = max_(
            0, taxable_income - ineligible_income
        )  # net capital gains eligble for alternative tax

        # ineligible_tax --- line 15
        statuses = filing_status.possible_values
        rate_p = parameters(period).gov.states.hi.tax.income.rates
        ineligible_tax = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.WIDOW,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                rate_p.single.calc(ineligible_income),
                rate_p.separate.calc(ineligible_income),
                rate_p.joint.calc(ineligible_income),
                rate_p.widow.calc(ineligible_income),
                rate_p.head_of_household.calc(ineligible_income),
            ],
        )

        # line 17
        alternative_tax = ineligible_tax + eligible_income * p.rate

        return eligibility * alternative_tax
