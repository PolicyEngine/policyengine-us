from policyengine_us.model_api import *
from policyengine_us.variables.household.expense.retirement._ira_supplied_contributions import (
    supplied_ira_contributions,
)


class ira_contribution_scale(Variable):
    value_type = float
    entity = Person
    label = "IRA contribution scale"
    unit = "/1"
    documentation = (
        "Scale factor applied to desired traditional and Roth IRA "
        "contributions when they exceed the combined IRA contribution limit. "
        "This preserves desired allocation shares rather than prioritizing "
        "either IRA type."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#b",
        "https://www.law.cornell.edu/uscode/text/26/408A#c_2",
    )

    def formula(person, period, parameters):
        # Supplied actual contributions use up the limit first; generated
        # contributions share what remains, in proportion to their desired
        # amounts.
        supplied = supplied_ira_contributions(person, period)
        supplied_own = 0
        generated_desired = 0
        for name, desired in (
            ("traditional_ira_contributions", "traditional_ira_contributions_desired"),
            ("roth_ira_contributions", "roth_ira_contributions_desired"),
        ):
            if supplied[name] is None:
                generated_desired = generated_desired + person(desired, period)
            else:
                supplied_own = supplied_own + max_(supplied[name], 0)
        available = max_(person("ira_contribution_limit", period) - supplied_own, 0)
        denominator = where(generated_desired > 0, generated_desired, 1)
        return min_(available / denominator, 1)
