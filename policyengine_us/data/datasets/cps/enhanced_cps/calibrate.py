import torch
import pandas as pd
import numpy as np
from policyengine_us import Microsimulation
import plotly.express as px
from tqdm import tqdm
from policyengine_core.data import Dataset
from policyengine_us.data import CPS_2023
import numpy as np
from policyengine_us import Microsimulation
import pandas as pd
from .process_puf import (
    FINANCIAL_SUBSET as FINANCIAL_VARIABLES,
    puf_imputed_cps_person_level,
)
from typing import Tuple


def generate_model_variables(dataset: str, time_period: str = "2023") -> Tuple:
    """Generates variables needed for the calibration process.

    Args:
        dataset (str): The name of the dataset to use.
        time_period (str, optional): The time period to use. Defaults to "2023".

    Returns:
        household_weights (torch.Tensor): The household weights.
        weight_adjustment (torch.Tensor): The weight adjustment.
        values_df (pd.DataFrame): A 2D array of values to transform household weights into statistical predictions.
        targets (dict): A dictionary of names and target values for the statistical predictions.
        targets_array (dict): A 1D array of target values for the statistical predictions.
        equivalisation_factors_array (dict): A 1D array of equivalisation factors for the statistical predictions to normalise the targets.
    """
    simulation = Microsimulation(dataset=dataset)
    simulation.default_calculation_period = time_period
    parameters = simulation.tax_benefit_system.parameters.calibration(
        f"{time_period}-01-01"
    )

    household_weights = torch.tensor(
        simulation.calculate("household_weight").values, dtype=torch.float32
    )
    weight_adjustment = torch.tensor(
        np.random.random(household_weights.shape) * 10,
        requires_grad=True,
        dtype=torch.float32,
    )

    values_df = pd.DataFrame()
    targets = {}
    equivalisation = {}

    # We need to normalise the targets. Common regression targets are often 1e1 to 1e3 (this informs the scale of the learning rate).
    COUNT_HOUSEHOLDS = household_weights.sum().item()
    FINANCIAL_EQUIVALISATION = COUNT_HOUSEHOLDS
    POPULATION_EQUIVALISATION = COUNT_HOUSEHOLDS / 1e5

    for variable_name in FINANCIAL_VARIABLES:
        if variable_name not in parameters.gov.irs.soi:
            continue
        label = (
            simulation.tax_benefit_system.variables[variable_name].label
            + " aggregate"
        )
        values_df[label] = simulation.calculate(
            variable_name, map_to="household"
        ).values
        targets[label] = parameters.gov.irs.soi[variable_name]
        equivalisation[label] = FINANCIAL_EQUIVALISATION

    # Program spending from CBO baseline projections

    PROGRAMS = [
        "income_tax",
        "snap",
        "social_security",
        "ssi",
        "unemployment_compensation",
    ]

    for variable_name in PROGRAMS:
        label = simulation.tax_benefit_system.variables[variable_name].label
        values_df[label] = simulation.calculate(
            variable_name, map_to="household"
        ).values
        targets[label] = parameters.gov.cbo[variable_name]
        equivalisation[label] = FINANCIAL_EQUIVALISATION

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
        equivalisation[f"{label} participants"] = POPULATION_EQUIVALISATION

    # Number of tax returns by AGI size

    agi_returns_thresholds = (
        parameters.gov.irs.soi.agi.number_of_returns.thresholds
    )
    agi_returns_values = parameters.gov.irs.soi.agi.number_of_returns.amounts
    agi = simulation.calculate("adjusted_gross_income").values
    is_filer = simulation.calculate("income_tax").values != 0
    for i in range(len(agi_returns_thresholds)):
        lower = agi_returns_thresholds[i]
        if i == len(agi_returns_thresholds) - 1:
            upper = np.inf
        else:
            upper = agi_returns_thresholds[i + 1]

        in_range = (agi >= lower) * (agi < upper) * is_filer
        household_returns_in_range = simulation.map_result(
            in_range, "tax_unit", "household"
        )

        name = f"Tax returns with ${lower:,.0f} <= AGI < ${upper:,.0f}"
        values_df[name] = household_returns_in_range
        targets[name] = agi_returns_values[i]
        equivalisation[name] = POPULATION_EQUIVALISATION
    # Total AGI aggregate by AGI band

    agi_returns_thresholds = parameters.gov.irs.soi.agi.total_agi.thresholds
    agi_returns_values = parameters.gov.irs.soi.agi.total_agi.amounts
    for i in range(len(agi_returns_thresholds)):
        lower = agi_returns_thresholds[i]
        if i == len(agi_returns_thresholds) - 1:
            upper = np.inf
        else:
            upper = agi_returns_thresholds[i + 1]

        in_range = (agi >= lower) * (agi < upper) * is_filer
        agi_in_range = agi * in_range
        household_agi_in_range = simulation.map_result(
            agi_in_range, "tax_unit", "household"
        )

        name = f"Total AGI from tax returns with ${lower:,.0f} <= AGI < ${upper:,.0f}"
        values_df[name] = household_agi_in_range
        targets[name] = agi_returns_values[i]
        equivalisation[name] = FINANCIAL_EQUIVALISATION

    # Total population
    values_df["U.S. population"] = simulation.calculate(
        "people", map_to="household"
    ).values
    targets["U.S. population"] = parameters.gov.census.populations.total
    equivalisation["U.S. population"] = POPULATION_EQUIVALISATION

    # Population by 10-year age group and sex
    age = simulation.calculate("age").values
    is_male = simulation.calculate("is_male")
    population_in_21 = simulation.tax_benefit_system.parameters.calibration.gov.census.populations.total(
        "2021-01-01"
    )
    population_growth = (
        parameters.gov.census.populations.total / population_in_21
    )
    for lower_age_group in range(0, 90, 10):
        for possible_is_male in (True, False):
            in_age_range = (age >= lower_age_group) & (
                age < lower_age_group + 5
            )
            in_sex_category = is_male == possible_is_male
            count_people_in_range = simulation.map_result(
                in_age_range * in_sex_category, "person", "household"
            )
            sex_category = "male" if possible_is_male else "female"
            name = f"{lower_age_group} to {lower_age_group + 5} and {sex_category} population"
            values_df[name] = count_people_in_range
            targets[name] = (
                household_weights.numpy() * count_people_in_range
            ).sum() * population_growth
            equivalisation[name] = POPULATION_EQUIVALISATION

    # Household population by number of adults and children

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
            name = f"{count_adults}-adult, {count_children}-child household population"
            values_df[name] = in_criteria
            targets[name] = (
                household_weights.numpy() * in_criteria
            ).sum() * population_growth
            equivalisation[name] = POPULATION_EQUIVALISATION

    # Tax filing unit counts by filing status

    filing_status = simulation.calculate("filing_status").values

    for filing_status_value in np.unique(filing_status):
        is_filing_status = filing_status == filing_status_value
        name = f"Filing status {filing_status_value.lower()} population"
        household_filing_status_unit_counts = simulation.map_result(
            is_filing_status, "tax_unit", "household"
        )
        values_df[name] = household_filing_status_unit_counts
        targets[name] = (
            household_weights.numpy() * household_filing_status_unit_counts
        ).sum() * population_growth
        equivalisation[name] = POPULATION_EQUIVALISATION

    targets_array = torch.tensor(list(targets.values()), dtype=torch.float32)
    equivalisation_factors_array = torch.tensor(
        list(equivalisation.values()), dtype=torch.float32
    )

    return (
        household_weights,
        weight_adjustment,
        values_df,
        targets,
        targets_array,
        equivalisation_factors_array,
    )


def aggregate(
    adjusted_weights: torch.Tensor, values: pd.DataFrame
) -> torch.Tensor:
    broadcasted_weights = adjusted_weights.reshape(-1, 1)
    weighted_values = torch.matmul(
        broadcasted_weights.T, torch.tensor(values.values, dtype=torch.float32)
    )
    return weighted_values


def calibrate(
    dataset: str,
    time_period: str = "2023",
    training_log_path: str = "training_log.csv.gz",
    learning_rate: float = 2e-1,
    epochs: int = 250_000,
) -> np.ndarray:
    (
        household_weights,
        weight_adjustment,
        values_df,
        targets,
        targets_array,
        equivalisation_factors_array,
    ) = generate_model_variables(dataset, time_period)
    training_log_df = pd.DataFrame()

    progress_bar = tqdm(range(epochs), desc="Calibrating weights")
    starting_loss = None
    for i in progress_bar:
        adjusted_weights = torch.relu(household_weights + weight_adjustment)
        result = (
            aggregate(adjusted_weights, values_df)
            / equivalisation_factors_array
        )
        loss = torch.mean(
            (result - targets_array / equivalisation_factors_array) ** 2
        )
        if i == 0:
            starting_loss = loss.item()
        loss.backward()
        if i % 20 == 0:
            current_loss = loss.item()
            progress_bar.set_description_str(
                f"Calibrating weights | Loss = {current_loss:,.0f}"
            )
            current_aggregates = (
                (result * equivalisation_factors_array).detach().numpy()[0]
            )
            training_log_df = pd.concat(
                [
                    training_log_df,
                    pd.DataFrame(
                        {
                            "name": list(targets.keys()) + ["total"],
                            "epoch": [i] * len(targets) + [i],
                            "value": list(current_aggregates) + [current_loss],
                            "target": list(targets.values()) + [0],
                            "time_period": time_period,
                        }
                    ),
                ]
            )
        weight_adjustment.data -= learning_rate * weight_adjustment.grad
        weight_adjustment.grad.zero_()

    training_log_df.to_csv(training_log_path, compression="gzip")

    loss_reduction = loss.item() / starting_loss - 1

    print(f"Loss reduction: {loss_reduction:.2%}")

    return adjusted_weights.detach().numpy()
