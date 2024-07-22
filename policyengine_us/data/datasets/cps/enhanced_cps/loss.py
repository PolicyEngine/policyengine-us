import pandas as pd
import numpy as np
from policyengine_us import Microsimulation
from policyengine_us.data.storage import STORAGE_FOLDER
from policyengine_us.data.datasets.cps.enhanced_cps.pe_to_soi import pe_to_soi
import pandas as pd
from .process_puf import FINANCIAL_SUBSET as FINANCIAL_VARIABLES
from typing import Tuple


def generate_model_variables(
    dataset: str, time_period: str = 2021, no_weight_adjustment: bool = False
) -> Tuple:
    """Generates variables needed for the calibration process.

    Args:
        dataset (str): The name of the dataset to use.
        time_period (str, optional): The time period to use. Defaults to "2022".
        no_weight_adjustment (bool, optional): Whether to skip the weight adjustment. Defaults to False.

    Returns:
        household_weights (torch.Tensor): The household weights.
        weight_adjustment (torch.Tensor): The weight adjustment.
        values_df (pd.DataFrame): A 2D array of values to transform household weights into statistical predictions.
        targets (dict): A dictionary of names and target values for the statistical predictions.
        targets_array (dict): A 1D array of target values for the statistical predictions.
        equivalisation_factors_array (dict): A 1D array of equivalisation factors for the statistical predictions to normalise the targets.
    """
    time_period = str(time_period)
    simulation = Microsimulation(dataset=dataset)
    simulation.default_calculation_period = time_period
    parameters = simulation.tax_benefit_system.parameters.calibration(
        f"{time_period}-01-01"
    )

    household_weights = simulation.calculate("household_weight").values
    weight_adjustment = np.random.random(household_weights.shape) * 10

    if no_weight_adjustment:
        weight_adjustment = np.zeros_like(household_weights)

    values_df = pd.DataFrame()
    targets = {}

    soi_subset = pd.read_csv(STORAGE_FOLDER / "soi.csv")

    df = pe_to_soi(dataset, time_period)
    agi = df["adjusted_gross_income"].values
    filer = df["is_tax_filer"].values
    soi_subset = soi_subset[soi_subset.Year == int(time_period)]
    agi_level_targeted_variables = [
        "adjusted_gross_income",
        "count",
        "employment_income",
    ]
    aggregate_level_targeted_variables = [
        "business_net_losses",
        "business_net_profits",
        "capital_gains_distributions",
        "capital_gains_gross",
        "capital_gains_losses",
        "estate_income",
        "estate_losses",
        "exempt_interest",
        "ira_distributions",
        "ordinary_dividends",
        "partnership_and_s_corp_income",
        "partnership_and_s_corp_losses",
        "qualified_dividends",
        "rent_and_royalty_net_income",
        "rent_and_royalty_net_losses",
        "taxable_interest_income",
        "taxable_pension_income",
        "taxable_social_security",
        "total_pension_income",
        "total_social_security",
        "unemployment_compensation",
    ]
    aggregate_level_targeted_variables = [
        variable
        for variable in aggregate_level_targeted_variables
        if variable in df.columns
    ]
    soi_subset = soi_subset[
        soi_subset.Variable.isin(agi_level_targeted_variables)
        & (
            (soi_subset["AGI lower bound"] != -np.inf)
            | (soi_subset["AGI upper bound"] != np.inf)
        )
        | (
            soi_subset.Variable.isin(aggregate_level_targeted_variables)
            & (soi_subset["AGI lower bound"] == -np.inf)
            & (soi_subset["AGI upper bound"] == np.inf)
        )
    ]
    for _, row in soi_subset.iterrows():
        if row["Taxable only"]:
            continue  # exclude "taxable returns" statistics

        mask = (
            (agi >= row["AGI lower bound"])
            * (agi < row["AGI upper bound"])
            * filer
        ) > 0

        if row["Filing status"] == "Single":
            mask *= df["filing_status"].values == "SINGLE"
        elif row["Filing status"] == "Married Filing Jointly/Surviving Spouse":
            mask *= df["filing_status"].values == "JOINT"
        elif row["Filing status"] == "Head of Household":
            mask *= df["filing_status"].values == "HEAD_OF_HOUSEHOLD"
        elif row["Filing status"] == "Married Filing Separately":
            mask *= df["filing_status"].values == "SEPARATE"

        values = df[row["Variable"]].values

        if row["Count"]:
            values = (values > 0).astype(float)

        agi_range_label = (
            f"{fmt(row['AGI lower bound'])}-{fmt(row['AGI upper bound'])}"
        )
        taxable_label = (
            "taxable" if row["Taxable only"] else "all" + " returns"
        )
        filing_status_label = row["Filing status"]

        variable_label = row["Variable"].replace("_", " ")

        if row["Count"] and not row["Variable"] == "count":
            label = (
                f"{variable_label}/count/AGI in "
                f"{agi_range_label}/{taxable_label}/{filing_status_label}"
            )
        elif row["Variable"] == "count":
            label = (
                f"{variable_label}/count/AGI in "
                f"{agi_range_label}/{taxable_label}/{filing_status_label}"
            )
        else:
            label = (
                f"{variable_label}/total/AGI in "
                f"{agi_range_label}/{taxable_label}/{filing_status_label}"
            )

        if label not in values_df.columns:
            values_df[label] = simulation.map_result(
                mask * values, "tax_unit", "household"
            )
            targets[label] = row["Value"]

    # Program spending from CBO baseline projections

    PROGRAMS = [
        # "income_tax",
        # "snap",
        "social_security",
        "ssi",
        "unemployment_compensation",
    ]

    for variable_name in PROGRAMS:
        label = (
            simulation.tax_benefit_system.variables[variable_name].label
            + " (CBO)"
        )
        values_df[label] = simulation.calculate(
            variable_name, map_to="household"
        ).values
        targets[label] = parameters.gov.cbo[variable_name]

    snap_participation = parameters.gov.usda.snap.participation
    ssi_participation = parameters.gov.ssa.ssi.participation
    ss_participation = parameters.gov.ssa.social_security.participation

    for program, participation in zip(
        ["snap", "ssi", "social_security"],
        [snap_participation, ssi_participation, ss_participation],
    ):
        label = simulation.tax_benefit_system.variables[program].label
        entity_level = simulation.tax_benefit_system.variables[
            program
        ].entity.key
        entity_level_value = simulation.calculate(program)
        values_df[f"{label} participants"] = simulation.map_result(
            entity_level_value > 0, entity_level, "household"
        )
        targets[f"{label} participants"] = participation

    demographics_sim = Microsimulation(dataset="cps_2022")

    # Total population
    values_df["U.S. population"] = simulation.calculate(
        "people", map_to="household"
    ).values
    targets["U.S. population"] = parameters.gov.census.populations.total

    # Population by 10-year age group and sex
    age_cps = demographics_sim.calculate("age").values
    is_male_cps = demographics_sim.calculate("is_male")
    age = simulation.calculate("age").values
    is_male = simulation.calculate("is_male")
    population_in_21 = demographics_sim.tax_benefit_system.parameters.calibration.gov.census.populations.total(
        "2021-01-01"
    )
    population_growth_since_21 = (
        parameters.gov.census.populations.total / population_in_21
    )
    cps_household_weights = demographics_sim.calculate(
        "household_weight"
    ).values
    for lower_age_group in range(0, 90, 10):
        for possible_is_male in (True, False):
            in_age_range = (age >= lower_age_group) & (
                age < lower_age_group + 5
            )
            in_sex_category = is_male == possible_is_male
            count_people_in_range = simulation.map_result(
                in_age_range * in_sex_category, "person", "household"
            )
            in_age_range_cps = (age_cps >= lower_age_group) & (
                age_cps < lower_age_group + 5
            )
            in_sex_category_cps = is_male_cps == possible_is_male
            count_people_in_range_cps = demographics_sim.map_result(
                in_age_range_cps * in_sex_category_cps, "person", "household"
            )
            count_people_in_range = simulation.map_result(
                in_age_range * in_sex_category, "person", "household"
            )
            sex_category = "male" if possible_is_male else "female"
            name = f"{lower_age_group} to {lower_age_group + 5} and {sex_category} population"
            values_df[name] = count_people_in_range
            targets[name] = (
                cps_household_weights * count_people_in_range_cps
            ).sum() * population_growth_since_21

    # Household population by number of adults and children

    household_count_adults_cps = demographics_sim.map_result(
        age_cps >= 18, "person", "household"
    )
    household_count_children_cps = demographics_sim.map_result(
        age_cps < 18, "person", "household"
    )

    household_count_adults = simulation.map_result(
        age >= 18, "person", "household"
    )
    household_count_children = simulation.map_result(
        age < 18, "person", "household"
    )

    for count_adults in range(1, 3):
        for count_children in range(0, 4):
            in_criteria = (
                (household_count_adults == count_adults)
                * (household_count_children == count_children)
                * 1.0
            )
            in_criteria_cps = (
                (household_count_adults_cps == count_adults)
                * (household_count_children_cps == count_children)
                * 1.0
            )
            name = f"{count_adults}-adult, {count_children}-child household population"
            values_df[name] = in_criteria
            targets[name] = (
                cps_household_weights * in_criteria_cps
            ).sum() * population_growth_since_21

    targets_array = np.array(list(targets.values()))

    return (
        household_weights,
        weight_adjustment,
        values_df,
        targets,
        targets_array,
    )


def aggregate_np(
    adjusted_weights: np.ndarray, values: pd.DataFrame
) -> np.ndarray:
    broadcasted_weights = adjusted_weights.reshape(-1, 1)
    weighted_values = np.matmul(broadcasted_weights.T, values.values)
    return weighted_values


def get_snapshot(
    dataset: str,
    time_period: str = 2021,
) -> pd.DataFrame:
    """Returns a snapshot of the training metrics without training the model.

    Args:
        dataset (str): The name of the dataset to use.
        time_period (str, optional): The time period to use. Defaults to "2022".

    Returns:
        pd.DataFrame: A DataFrame containing the training metrics.
    """
    print(dataset, time_period)
    (
        household_weights,
        weight_adjustment,
        values_df,
        targets,
        targets_array,
    ) = generate_model_variables(
        dataset, time_period, no_weight_adjustment=True
    )
    adjusted_weights = np.maximum(household_weights + weight_adjustment, 0)
    result = aggregate_np(adjusted_weights, values_df)
    target = targets_array
    current_aggregates = result[0]
    loss = np.mean((((result + 1) / (target + 1) - 1) ** 2))
    current_loss = loss.item()
    return pd.DataFrame(
        {
            "name": list(targets.keys()) + ["total"],
            "value": list(current_aggregates) + [current_loss],
            "target": list(targets.values()) + [0],
            "time_period": time_period,
        }
    )


def fmt(x):
    if x == -np.inf:
        return "-inf"
    if x == np.inf:
        return "inf"
    if x < 1e3:
        return f"{x:.0f}"
    if x < 1e6:
        return f"{x/1e3:.0f}k"
    if x < 1e9:
        return f"{x/1e6:.0f}m"
    return f"{x/1e9:.1f}bn"
