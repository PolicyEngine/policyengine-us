from policyengine_us.model_api import *

# FIXME: This is boilerplate taken directly from the reform code.


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
        ).gov.states.co.tax.income.credits.family_affordability
        base_amount = p.amount * dependent
        agi = person.tax_unit("adjusted_gross_income", period)
        filing_status = person.tax_unit("filing_status", period)
        reduction_threshold = p.reduction.threshold[filing_status]
        excess = max_(agi - reduction_threshold, 0)
        increments = np.ceil(excess / p.reduction.increment)
        percent_reduction = min_(increments * p.reduction.rate, 1)
        age_multiplier = p.age_multiplier.calc(age)
        return base_amount * age_multiplier * (1 - percent_reduction)
