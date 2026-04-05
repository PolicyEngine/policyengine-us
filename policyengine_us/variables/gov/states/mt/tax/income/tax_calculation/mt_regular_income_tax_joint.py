from policyengine_us.model_api import *


class mt_regular_income_tax_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income (subtracting capital gains since 2024) tax before refundable credits, when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.main
        taxable_income = add(tax_unit, period, ["mt_taxable_income_joint"])
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        if p.capital_gains.in_effect:
            ltcg = add(tax_unit, period, ["long_term_capital_gains"])
            stcg = add(tax_unit, period, ["short_term_capital_gains"])
            net_cg = ltcg + stcg
            # Montana Form 2 line 2 uses the federal net long-term capital gain
            # amount, which is limited by any short-term capital losses.
            cg_to_subtract = max_(min_(ltcg, net_cg), 0)
            taxable_income = max_(taxable_income - cg_to_subtract, 0)
        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(taxable_income),
                p.joint.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
                p.separate.calc(taxable_income),
                p.surviving_spouse.calc(taxable_income),
            ],
        )
