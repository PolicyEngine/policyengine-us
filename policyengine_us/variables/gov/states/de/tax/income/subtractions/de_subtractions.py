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
        total_subtractions = add(person, period, p.subtractions)
        # A tax unit dependent's U.S. government interest is on the dependent's
        # own return and never in the filer's federal AGI, so it is not
        # subtracted here, where each person's amounts are summed into the
        # filer's.
        if "us_govt_interest_person" in p.subtractions:
            dependent = person("is_tax_unit_dependent", period)
            total_subtractions = total_subtractions - dependent * person(
                "us_govt_interest_person", period
            )
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
