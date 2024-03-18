from policyengine_us.data.storage import STORAGE_FOLDER
from policyengine_core.data import Dataset
import pandas as pd
from policyengine_us.data.datasets.cps.enhanced_cps.calibrated_cps import (
    CalibratedPUFExtendedCPS_2022,
)


class EnhancedCPS(Dataset):
    data_format = Dataset.TIME_PERIOD_ARRAYS
    time_period = None
    num_years: int = None
    input_dataset = None

    def generate(self):
        self.remove()
        new_data = {}
        cps = self.input_dataset()
        from policyengine_us.data.datasets.cps.cps import (
            CPS_2019,
        )  # Always use CPS 2019 for previous year imputations

        cps_data = cps.load()
        for variable in cps.variables:
            new_data[variable] = {}
            for time_period in cps_data[variable]:
                new_data[variable][time_period] = cps_data[variable][
                    time_period
                ][...]

        # Add imputation of prior year income
        from policyengine_us import Microsimulation

        sim = Microsimulation(dataset=CPS_2019)

        VARIABLES = [
            "previous_year_income_available",
            "employment_income",
            "self_employment_income",
            "age",
            "is_male",
            "spm_unit_state_fips",
            "dividend_income",
            "interest_income",
            "social_security",
            "capital_gains",
            "is_disabled",
            "is_blind",
            "is_married",
            "tax_unit_children",
            "pension_income",
        ]

        OUTPUTS = [
            "employment_income_last_year",
            "self_employment_income_last_year",
        ]

        df = sim.calculate_dataframe(
            VARIABLES + OUTPUTS, 2019, map_to="person"
        )
        df_train = df[df.previous_year_income_available]

        from survey_enhance import Imputation

        income_last_year = Imputation()
        X = df_train[VARIABLES[1:]]
        y = df_train[OUTPUTS]

        income_last_year.train(X, y)

        sim = Microsimulation(dataset=cps)

        df = sim.calculate_dataframe(
            VARIABLES + OUTPUTS, self.time_period, map_to="person"
        )

        parameters = sim.tax_benefit_system.parameters

        new_data["employment_income_last_year"] = {}
        new_data["self_employment_income_last_year"] = {}

        for time_period in range(
            self.time_period, self.time_period + self.num_years
        ):
            projections = parameters(
                f"{time_period - 1}-01-01"
            ).calibration.gov.irs.soi
            quantiles = income_last_year.solve_for_mean_quantiles(
                [
                    projections.employment_income,
                    projections.self_employment_income,
                ],
                df[VARIABLES[1:]],
                sim.calculate(
                    "household_weight", time_period, map_to="person"
                ).values,
                max_iterations=6,
            )

            y_pred = income_last_year.predict(
                df.drop(columns=OUTPUTS), mean_quantile=quantiles
            )

            df[OUTPUTS] = y_pred[OUTPUTS]
            new_data["employment_income_last_year"][time_period] = df[
                "employment_income_last_year"
            ].values
            new_data["self_employment_income_last_year"][time_period] = df[
                "self_employment_income_last_year"
            ].values

        self.save_dataset(new_data)


class EnhancedCPS_2022(EnhancedCPS):
    name = "enhanced_cps_2022"
    label = "Enhanced CPS (2022-25)"
    input_dataset = CalibratedPUFExtendedCPS_2022
    time_period = 2022
    num_years = 4
    file_path = STORAGE_FOLDER / "enhanced_cps_2022.h5"
    url = "release://policyengine/policyengine-us/enhanced-cps-2023/enhanced_cps.h5"
