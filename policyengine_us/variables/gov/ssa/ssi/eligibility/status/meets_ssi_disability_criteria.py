from policyengine_us.model_api import *


class meets_ssi_disability_criteria(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = (
        "Indicates whether a person meets the Supplemental Security Income "
        "disability criteria before the substantial gainful activity screen"
    )
    label = "Meets SSI disability criteria"
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#a_3_A"

    def formula(person, period, parameters):
        holder = person.simulation.get_holder("meets_ssi_disability_criteria")
        prior_periods = [
            known_period
            for known_period in holder.get_known_periods()
            if known_period.unit == YEAR and known_period.start < period.start
        ]
        if prior_periods:
            latest_period = max(
                prior_periods, key=lambda known_period: known_period.start
            )
            latest_value = holder.get_array(
                latest_period, person.simulation.branch_name
            )
            latest_broad_disability = person("is_disabled", latest_period)
            # Data-backed overrides should persist across analysis years; pure
            # formula caches should not shadow later is_disabled inputs.
            if not np.array_equal(latest_value, latest_broad_disability):
                return None

        return person("is_disabled", period)
