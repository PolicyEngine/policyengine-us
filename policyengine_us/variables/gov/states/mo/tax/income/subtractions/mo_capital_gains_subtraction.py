from policyengine_us.model_api import *


class mo_capital_gains_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Missouri capital gains subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/faq/taxation/individual/capital-gains-subtraction.html",  # MO form MO-A
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        ltcg = add(tax_unit, period, ["long_term_capital_gains"])
        stcg = add(tax_unit, period, ["short_term_capital_gains"])
        capped_stcg = min_(0, stcg)
        net_cg = max_(0, ltcg + capped_stcg)
        p = parameters(
            period
        ).gov.states.mo.tax.income.deductions.net_capital_gain
        return net_cg * p.rate
