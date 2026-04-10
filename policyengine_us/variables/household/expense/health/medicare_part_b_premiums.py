from policyengine_us.model_api import *


class medicare_part_b_premiums(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premiums"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        # Backward-compatibility: preserve legacy direct inputs on
        # medicare_part_b_premiums if callers still provide them.
        holder = person.simulation.get_holder("medicare_part_b_premiums")
        known_periods = holder.get_known_periods()
        if known_periods:
            if period in known_periods:
                current_input = holder.get_array(period)
                if current_input is not None:
                    return current_input

            eligible_periods = sorted(
                known_period
                for known_period in known_periods
                if known_period.start < period.start
            )
            if eligible_periods:
                last_known_period = eligible_periods[-1]
                last_known_value = holder.get_array(last_known_period)
                if last_known_value is not None:
                    moop_per_capita = parameters(period).calibration.gov.hhs.cms.moop_per_capita
                    last_known_moop_per_capita = parameters(
                        last_known_period
                    ).calibration.gov.hhs.cms.moop_per_capita
                    return (
                        last_known_value
                        * moop_per_capita
                        / last_known_moop_per_capita
                    )

        enrolled = person("medicare_enrolled", period)
        gross_premium = person("income_adjusted_part_b_premium", period)
        msp_coverage = person("msp_part_b_premium_coverage", period)
        return max_(where(enrolled, gross_premium, 0) - msp_coverage, 0)
