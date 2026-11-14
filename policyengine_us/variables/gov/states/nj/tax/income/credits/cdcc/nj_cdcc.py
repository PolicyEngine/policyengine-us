from policyengine_us.model_api import *


class nj_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey CDCC"
    documentation = "New Jersey Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=44",
        "https://pub.njleg.state.nj.us/Bills/2018/PL18/45_.HTM",
        "https://pub.njleg.state.nj.us/Bills/2020/PL21/308_.HTM",
    )
    defined_for = StateCode.NJ

    def formula_2018(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.cdcc
        taxable_income = tax_unit("nj_taxable_income", period)
        federal_cdcc = tax_unit("cdcc", period)
        qualifying_people = tax_unit("count_cdcc_eligible", period)
        rate = p.rate.calc(taxable_income, right=True)
        maximum = p.max_amount.calc(qualifying_people)
        return min_(federal_cdcc * rate, maximum)

    def formula_2021(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.cdcc.rate
        taxable_income = tax_unit("nj_taxable_income", period)
        federal_cdcc = tax_unit("cdcc", period)
        return federal_cdcc * p.calc(taxable_income, right=True)
