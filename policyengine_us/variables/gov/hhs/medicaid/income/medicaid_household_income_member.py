from policyengine_us.model_api import *


class medicaid_household_income_member(Variable):
    value_type = float
    entity = Person
    label = "Countable person income for Medicaid MAGI household income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#d"

    def formula(person, period, parameters):
        excluded = person("medicaid_non_filer_child_age_eligible", period) & ~person(
            "medicaid_person_is_required_to_file", period
        )

        return where(excluded, 0, person("medicaid_magi_person", period))
