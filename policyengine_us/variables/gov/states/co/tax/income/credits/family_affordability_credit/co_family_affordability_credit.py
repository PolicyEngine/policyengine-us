from policyengine_us.model_api import *

#FIXME: This is boilerplate taken directly from the reform code.

class co_family_affordability_credit(Variable):
    value_type = float
    entity = Person
    label = "Colorado Family Affordability Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://leg.colorado.gov/bills/hb24-1311"
    defined_for = StateCode.CO
    def formula(person, period, parameters):
        age = person("age", period)
        dependent = person("is_child_dependent", period)
        p = parameters(
            period
        ).gov.states.co.tax.income.credits.family_affordability_credit
        base_amount = p.amount * dependent
        age_reduction = p.age_reduction.calc(age) / 100
        agi = person.tax_unit("adjusted_gross_income", period)
        filing_status = person.tax_unit("filing_status", period)
        phase_out_start = p.income_reduction.start[filing_status]
        phase_out_amount = p.income_reduction.amount
        phase_out_increment = p.income_reduction.increment
        excess = max_(agi - phase_out_start, 0)
        increments = np.ceil(excess / phase_out_increment)
        amount = increments * phase_out_amount
        income_reduction = max_(100 - amount, 0) / 100
        return base_amount * age_reduction * income_reduction