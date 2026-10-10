from policyengine_us.model_api import *

# FIXME: This is boilerplate taken directly from the reform code.


class co_family_affordability_credit(Variable):
    value_type = float
    entity = Person
    label = "Colorado Family Affordability Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://leg.colorado.gov/bills/hb24-1311",
        # Income Tax Topics: Family Affordability Tax Credit (January 2026).
        "https://tax.colorado.gov/sites/tax/files/documents/ITT_Family_Affordability_Tax_Credit_Jan_2026.pdf#page=1",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        age = person("age", period)
        # The child must meet the federal child tax credit's dependent
        # requirement; a return on which the filer (or, if joint, either
        # spouse) can be claimed as a dependent has no dependents (IRC
        # 152(b)(1)).
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        dependent = (
            person("is_qualifying_child_dependent", period) & ~filer_is_dependent
        )
        p = parameters(period).gov.states.co.tax.income.credits.family_affordability
        base_amount = p.amount * dependent
        agi = person.tax_unit("adjusted_gross_income", period)
        filing_status = person.tax_unit("filing_status", period)
        reduction_threshold = p.reduction.threshold[filing_status]
        excess = max_(agi - reduction_threshold, 0)
        increments = np.ceil(excess / p.reduction.increment)
        percent_reduction = min_(increments * p.reduction.rate, 1)
        age_multiplier = p.age_multiplier.calc(age)
        return base_amount * age_multiplier * (1 - percent_reduction)
