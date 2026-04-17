from policyengine_us.model_api import *


class mt_regular_income_tax_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana income (subtracting capital gains before 2024) tax before refundable credits, when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.main
        taxable_income = person("mt_taxable_income_indiv", period)
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        if p.capital_gains.in_effect:
            ltcg = person("long_term_capital_gains", period)
            stcg = person("short_term_capital_gains", period)
            net_cg = ltcg + stcg
            # Montana Form 2 line 2 uses the federal net long-term capital gain
            # amount, which is limited by any short-term capital losses.
            cg_to_subtract = max_(min_(ltcg, net_cg), 0)
            taxable_income = max_(taxable_income - cg_to_subtract, 0)
        status = filing_status.possible_values
        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
                p.separate.calc(taxable_income),
                p.surviving_spouse.calc(taxable_income),
            ],
        )
