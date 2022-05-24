from openfisca_us.model_api import *


class three_digit_zip_code(Variable):
    value_type = str
    entity = Household
    label = "Three-digit zipcode"
    definition_period = YEAR

    def formula(household, period, parameters):
        zip_code = household("zip_code", period)
        if any(zip_code == "UNKNOWN"):
            # We don't have full zip codes - randomly assign zip codes
            population_data = parameters(
                period
            ).demographic.geography.population_by_three_digit_zip_code
            zip_codes = np.array(list(population_data._children.keys()))
            populations = np.array(list(population_data._children.values()))
            zip_code = (
                np.random.choice(
                    zip_codes,
                    size=len(zip_code),
                    p=populations / populations.sum(),
                )
                .astype(int)
                .astype(str)
            )
        else:
            zip_code = (zip_code.astype(int) // 1e2).astype(int).astype(str)
        return np.char.zfill(zip_code, 3)
