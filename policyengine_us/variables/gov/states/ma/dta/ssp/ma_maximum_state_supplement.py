from policyengine_us.model_api import *


class ma_maximum_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts maximum State Supplement payment amount"
    unit = USD
    definition_period = YEAR
    defined_for = "is_ssi_eligible_individual"

    def formula(person, period, parameters):
        """
        Returns the maximum annual state supplement for an SSI-eligible individual,
        before subtracting any leftover income. Depends on:
          - The person's state of residence
          - Living arrangement (e.g. FULL_COST, REST_HOME, etc.)
          - Category (Aged, Blind, or Disabled)
          - Single vs. Joint claim (couple)
        """

        # 1. Get state and living arrangement from the person's household.
        living_arrangement = person.household(
            "ma_state_living_arrangement", period
        )

        # 2. Load the state's parameter dictionary. This is structured like:
        # p[living_arrangement][category][("1" or "2")] = monthly rate
        p = parameters(period).gov.states.ma.dta.ssp.amount
        # For example: p["FULL_COST"]["AGED"]["1"] = 128.82

        # 3. Retrieve the sub-dict for this person's state & living arrangement
        # e.g. amounts = p["FULL_COST"]
        amounts_for_state_la = p[living_arrangement]

        # 4. Identify whether the person is aged, blind, or disabled.
        #    (It's possible to be both aged+blind, so we might pick whichever rate is higher.)
        is_blind = person("is_blind", period)
        is_aged = person("is_ssi_aged", period)
        is_disabled = person("is_ssi_disabled", period)

        # 5. We'll build an array of the single or double (couple) label: e.g. "1" or "2".
        #    This matches the structure in the parameter file.
        joint_claim = person("ssi_claim_is_joint", period)
        # Convert True -> "2", False -> "1"
        single_or_double_str = where(joint_claim, 2, 1).astype(str)

        # 6. For vectorization, we note how many people are in the array dimension.
        #    We do the same trick for categories. For each person, we might pick
        #    'AGED', 'BLIND', or 'DISABLED' monthly rate. This code uses np arrays:
        ssi_categories = person("ssi_category", period).possible_values
        count_persons = len(is_blind)  # number of entries in the vector

        # 7. Create arrays for each category's monthly rate. For each person, we do:
        #    amounts_for_state_la["AGED"]["1"], amounts_for_state_la["AGED"]["2"], etc.
        #    Then multiply by the boolean (is_aged, is_blind, is_disabled).
        #    We use max_() to pick whichever is relevant if more than one category is true.

        monthly_aged_rate = (
            amounts_for_state_la[
                np.array([ssi_categories.AGED] * count_persons)
            ][single_or_double_str]
            * is_aged
        )

        monthly_blind_rate = (
            amounts_for_state_la[
                np.array([ssi_categories.BLIND] * count_persons)
            ][single_or_double_str]
            * is_blind
        )

        monthly_disabled_rate = (
            amounts_for_state_la[
                np.array([ssi_categories.DISABLED] * count_persons)
            ][single_or_double_str]
            * is_disabled
        )

        # 8. We'll pick the maximum, so if someone's "is_aged" is True and "is_blind" is False,
        #    the first product is nonzero, second is zero, etc.
        #    If they're both true, we pick whichever is higher.
        monthly_rate = np.maximum.reduce(
            [monthly_aged_rate, monthly_blind_rate, monthly_disabled_rate]
        )

        # 9. Multiply by 12 to get an annual figure. This is the maximum annual supplement
        #    (still for each person individually).
        annual_rate = monthly_rate * MONTHS_IN_YEAR

        # 10. Summation across the marital unit. If we have a couple, we might want
        #     the total combined amount, then split it. Or we might directly keep it as per-person.
        # Here, they sum for the entire marital unit, then later they do dividing if needed.
        combined_amount_for_marital_unit = person.marital_unit.sum(annual_rate)

        # 11. Finally, the code divides by 2 if it's a joint claim, presumably so that
        #     each person sees their half. If it's not joint, it just returns the full amount.
        # This "per-person" approach might be confusing if the state has a special "couple rate"
        # that isn't exactly double or half. But that's how the code is set up now.
        divisor = where(joint_claim, 2, 1)
        return combined_amount_for_marital_unit / divisor
