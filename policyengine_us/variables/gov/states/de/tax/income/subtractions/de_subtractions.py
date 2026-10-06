from policyengine_us.model_api import *


class de_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Delaware subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.income.subtractions
        # Each person's net income is summed into the filer's (de_agi_joint),
        # so a tax unit dependent gets none of these. The income items are
        # subtracted "to the extent included in federal adjusted gross income"
        # (30 Del. C. 1106(b)(4), (9), (10)), which leaves a dependent's income
        # out, and the 529 subtraction is for amounts "contributed by an
        # individual" or, on a joint return, "by the spouses" ((b)(11)).
        total_subtractions = person_non_dep_add(person, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
