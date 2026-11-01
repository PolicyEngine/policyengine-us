from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class is_older_child_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid older child financial criteria"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.118",
        # Page 1: the 138%/266%/322% FPL monthly dollar table.
        "https://www.dhcs.ca.gov/services/HACCP/Documents/Program-Income-Eligibility-Comparison2025.pdf#page=1",
        # Page 2: footnotes 3-4 defining the inclusive "up to 266%" and
        # "above 266%" income bands.
        "https://www.dhcs.ca.gov/services/HACCP/Documents/Program-Income-Eligibility-Comparison2025.pdf#page=2",
    )

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.older_child
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        return medicaid_income_eligible(person, period, parameters, income_limit)
