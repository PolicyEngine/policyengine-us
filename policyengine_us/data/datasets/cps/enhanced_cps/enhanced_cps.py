from policyengine_us.data.storage import STORAGE_FOLDER
from policyengine_core.data import Dataset
import pandas as pd


class CalibratedPUFExtendedCPS(Dataset):
    name = "calibrated_puf_extended_cps"
    label = "Calibrated PUF-extended CPS (2023)"
    file_path = STORAGE_FOLDER / "calibrated_puf_extended_cps.h5"
    data_format = Dataset.TIME_PERIOD_ARRAYS
    time_period = 2023
    num_years: int = 3

    def generate(self):
        from .calibrate import calibrate
        from .puf_extended_cps import PUFExtendedCPS_2023

        new_data = {}
        cps = PUFExtendedCPS_2023()
        cps_data = cps.load()
        for year in range(self.time_period, self.time_period + self.num_years):
            year = str(year)
            adjusted_weights = calibrate(
                "puf_extended_cps_2023",
                time_period=year,
                training_log_path="calibration_log.csv.gz",
            )
            for variable in cps.variables:
                if variable not in new_data:
                    new_data[variable] = {}
                if variable == "household_weight":
                    new_data[variable][year] = adjusted_weights
                elif "_weight" not in variable and (
                    (year == str(self.time_period)) or ("_id" in variable)
                ):
                    new_data[variable][year] = cps_data[variable][...]

        self.save_dataset(new_data)


class EnhancedCPS_2023(Dataset):
    name = "enhanced_cps_2023"
    label = "Enhanced CPS (2023)"
    file_path = STORAGE_FOLDER / "enhanced_cps.h5"
    data_format = Dataset.TIME_PERIOD_ARRAYS
    time_period = 2023
    num_years: int = 3
    url = "release://policyengine/policyengine-us/enhanced-cps-2023/enhanced_cps.h5"

    def generate(self):
        self.remove()
        new_data = {}
        cps = CalibratedPUFExtendedCPS()
        from policyengine_us.data.datasets.cps.cps import CPS_2019

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
            VARIABLES + OUTPUTS, 2023, map_to="person"
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
                max_iterations=7,
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
