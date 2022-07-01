from openfisca_us.model_api import *


class medicaid_rating_area(Variable):
    value_type = int
    entity = Household
    label = "Medicaid rating area"
    definition_period = YEAR

    def formula(household, period, parameters):
        mra = parameters(
            period
        ).gov.hhs.medicaid.geography.medicaid_rating_area
        state = household("state_code_str", period)
        has_defined_mra = pd.Series(state).isin(mra._children)
        state = where(
            has_defined_mra, state, list(mra._children.keys())[0]
        )  # Fill in with any valid State to avoid errors
        three_digit_zip_code = household("three_digit_zip_code", period)
        mra_values = np.ones_like(state) * -1
        for individual_state in mra._children.keys():
            in_state = state == individual_state
            if any(in_state):
                mra_values[in_state] = getattr(
                    mra, individual_state,
                )[three_digit_zip_code[in_state]]
        return mra_values # We'd usually avoid the 'return variable' pattern, but it's unavoidable here.
