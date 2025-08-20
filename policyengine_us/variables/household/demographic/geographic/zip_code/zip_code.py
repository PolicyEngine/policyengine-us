from policyengine_us.model_api import *
from policyengine_us.data import ZIP_CODE_DATASET


class zip_code(Variable):
    value_type = str
    entity = Household
    label = "ZIP code"
    definition_period = YEAR
    default_value = "UNKNOWN"

    def formula(household, period, parameters):
        state_code = household("state_code_str", period)

        if household.simulation.has_axes:
            # For each state, select ONE zip code randomly, with probability proportional to population.

            state_to_zip_code = {
                state_code: ZIP_CODE_DATASET[
                    ZIP_CODE_DATASET.state == state_code
                ]
                .sample(1, weights="population")
                .zip_code.iloc[0]
                for state_code in ZIP_CODE_DATASET.state.unique()
            }

            household_zip_code = (
                pd.Series(state_code).map(state_to_zip_code).squeeze()
            )

        else:
            household_zip_code = np.empty_like(state_code, dtype=object)
            for state in ZIP_CODE_DATASET.state.unique():
                count_households_in_state = (state_code == state).sum()
                household_zip_code[state_code == state] = (
                    ZIP_CODE_DATASET[ZIP_CODE_DATASET.state == state]
                    .sample(
                        count_households_in_state,
                        weights="population",
                        random_state=192837465,
                        replace=True,
                    )
                    .zip_code
                )
            household_zip_code = pd.Series(household_zip_code)

        return household_zip_code.astype(str).str.zfill(5)
