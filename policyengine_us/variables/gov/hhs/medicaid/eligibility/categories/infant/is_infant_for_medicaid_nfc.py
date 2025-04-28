from policyengine_us.model_api import *


class is_infant_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid infant non-financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.infant
        age = person("age", period)
        state_code = person.household("state_code_str", period)

        # Use vectorized selection (similar to the example) to choose which calculation to use
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.infant.age_range
        return select(
            [state_code == "CA", state_code == "MN"],
            [p.in_ca.calc(age), p.in_mn.calc(age)],
            default=p.other.calc(age),
        )
