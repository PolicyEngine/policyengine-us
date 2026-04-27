from policyengine_us.model_api import *
from policyengine_core import periods


def _get_explicit_legacy_part_b_inputs(person):
    situation_input = getattr(person.simulation, "situation_input", None)
    if not isinstance(situation_input, dict):
        return {}

    people_inputs = situation_input.get("people")
    if not isinstance(people_inputs, dict):
        return {}

    explicit_inputs = {}
    for person_index, person_id in enumerate(person.ids):
        person_input = people_inputs.get(person_id)
        if not isinstance(person_input, dict):
            continue
        legacy_values = person_input.get("medicare_part_b_premiums")
        if not isinstance(legacy_values, dict):
            continue

        for period_str, value in legacy_values.items():
            period_obj = periods.period(period_str)
            period_inputs = explicit_inputs.setdefault(
                period_obj, np.full(person.count, np.nan)
            )
            period_inputs[person_index] = value

    return explicit_inputs


class medicare_part_b_premiums(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premiums"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        # Backward-compatibility: preserve legacy direct inputs on
        # medicare_part_b_premiums if callers still provide them.
        enrolled = person("medicare_enrolled", period)
        gross_premium = person("income_adjusted_part_b_premium", period)
        msp_coverage = person("msp_part_b_premium_coverage", period)
        modeled_value = max_(where(enrolled, gross_premium, 0) - msp_coverage, 0)

        explicit_inputs = _get_explicit_legacy_part_b_inputs(person)
        if period in explicit_inputs:
            current_input = explicit_inputs[period]
            current_mask = ~np.isnan(current_input)
            return where(current_mask, current_input, modeled_value)

        eligible_periods = sorted(
            known_period
            for known_period in explicit_inputs
            if known_period.start < period.start
        )
        if not eligible_periods:
            return modeled_value

        last_known_period = eligible_periods[-1]
        last_known_value = explicit_inputs[last_known_period]
        legacy_mask = ~np.isnan(last_known_value)
        if not legacy_mask.any():
            return modeled_value

        moop_per_capita = parameters(period).calibration.gov.hhs.cms.moop_per_capita
        last_known_moop_per_capita = parameters(
            last_known_period
        ).calibration.gov.hhs.cms.moop_per_capita
        uprated_legacy_value = (
            last_known_value * moop_per_capita / last_known_moop_per_capita
        )
        return where(legacy_mask, uprated_legacy_value, modeled_value)
