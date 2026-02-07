from policyengine_us.model_api import *


class is_ssdi_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Is SSDI eligible"
    definition_period = YEAR
    reference = "https://www.ssa.gov/benefits/disability/"
    documentation = """
    Determines if a person is eligible for Social Security Disability Insurance (SSDI).
    Requires meeting disability criteria, work history requirements, and not engaging in SGA.
    """

    def formula(person, period, parameters):
        # Must be disabled
        is_disabled = person("is_ssdi_disabled", period)

        # Must meet work history requirements
        meets_work_history = person(
            "meets_ssdi_work_history_requirements", period
        )

        # Must not be engaged in substantial gainful activity
        not_engaged_in_sga = ~person("ssdi_engaged_in_sga", period)

        # Must have waited the required period (handled separately in benefit calculation)
        # This would typically check months since disability onset

        return is_disabled & meets_work_history & not_engaged_in_sga
