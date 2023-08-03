from policyengine_us.model_api import *


class maximum_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "Maximum State Supplement"
    unit = USD
    definition_period = YEAR
    defined_for = "is_ssi_eligible_individual"

    def formula_2022(person, period, parameters):
        marital_unit = person.marital_unit
        eligible = person("is_ssi_eligible_individual", period)
        state_code = person.household("state_code_str", period)
        living_arrangement = person.household(
            "state_living_arrangement", period
        )
        ss_amounts = parameters(period).gov.ssa.state_supplement.amount
        amounts = ss_amounts[state_code][living_arrangement]
        is_blind = person("is_blind", period)
        is_aged = person("is_ssi_aged", period)
        is_disabled = person("is_ssi_disabled", period)
        count_persons = len(is_blind)
        ssi_categories = person("ssi_category", period).possible_values
        joint_claim = person("ssi_claim_is_joint", period)
        count_eligible_str = where(joint_claim, 2, 1).astype(str)
        per_person_amount = (
            max_(
                amounts[np.array([ssi_categories.AGED] * count_persons)][
                    count_eligible_str
                ]
                * is_aged,
                amounts[np.array([ssi_categories.BLIND] * count_persons)][
                    count_eligible_str
                ]
                * is_blind,
                amounts[np.array([ssi_categories.DISABLED] * count_persons)][
                    count_eligible_str
                ]
                * is_disabled,
            )
            * MONTHS_IN_YEAR
        )
        combined_amount = marital_unit.sum(per_person_amount)
        return eligible * combined_amount * where(joint_claim, 1 / 2, 1)
