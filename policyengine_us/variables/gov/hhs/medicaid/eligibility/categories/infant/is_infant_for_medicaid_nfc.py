from policyengine_us.model_api import *


class is_infant_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid infant non-financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)  # person’s age in years
        state = person.household("state_code_str", period)

        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.infant.age_range

        # Pick the right upper-bound age for this state
        upper_bound = select(
            [state == "CA", state == "MN"],
            [p.in_ca, p.in_mn],  #
            default=p.other,
        )

        return age < upper_bound
