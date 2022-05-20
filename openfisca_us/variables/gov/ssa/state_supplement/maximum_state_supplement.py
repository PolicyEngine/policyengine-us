from openfisca_us.model_api import *

from openfisca_core.parameters import VectorialParameterNodeAtInstant


class maximum_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "Maximum State Supplement"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        marital_unit = person.marital_unit
        eligible = person("is_ssi_aged_blind_disabled", period)
        num_eligible = marital_unit.sum(eligible)
        state_code = person.household("state_code_str", period)
        living_arrangement = person.household(
            "state_living_arrangement", period
        )
        ss_amounts = parameters(period).ssa.state_supplement.amount
        amounts = ss_amounts[state_code][living_arrangement]
        is_blind = person("is_blind", period)
        is_aged = person("is_ssi_aged", period)
        is_disabled = person("is_ssi_disabled", period)
        num_persons = len(is_blind)
        ssi_categories = person("ssi_category", period).possible_values
        num_eligible_str = clip(num_eligible.astype(int), 1, 2).astype(str)
        per_person_amount = (
            max_(
                amounts[np.array([ssi_categories.AGED] * num_persons)][
                    num_eligible_str
                ]
                * is_aged,
                amounts[np.array([ssi_categories.BLIND] * num_persons)][
                    num_eligible_str
                ]
                * is_blind,
                amounts[np.array([ssi_categories.DISABLED] * num_persons)][
                    num_eligible_str
                ]
                * is_disabled,
            )
            * MONTHS_IN_YEAR
        )
        combined_amount = marital_unit.sum(per_person_amount)
        return eligible * combined_amount * where(num_eligible > 1, 1 / 2, 1)
