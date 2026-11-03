from policyengine_us.model_api import *


class ssi_unearned_income_deemed_from_ineligible_parent(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income (deemed from ineligible parent)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1165"

    def formula(person, period, parameters):
        # Sum completed monthly budgets; supplied amounts retain their annual basis.
        return person(
            "ssi_unearned_income_deemed_from_ineligible_parent_monthly", period
        )
