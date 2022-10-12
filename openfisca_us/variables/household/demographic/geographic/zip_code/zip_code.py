from policyengine_us.model_api import *


class zip_code(Variable):
    value_type = str
    entity = Household
    label = "ZIP code"
    definition_period = ETERNITY
    default_value = "UNKNOWN"

    def formula(household, period, parameters):
        numeric_zip_code = ZIP_CODE_DATASET.zip_code.sample(
            household.count, weights=ZIP_CODE_DATASET.population, replace=True
        )
        return numeric_zip_code.astype(str).str.zfill(5)
