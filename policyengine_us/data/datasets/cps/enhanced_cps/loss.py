import pandas as pd
import numpy as np
from policyengine_us import Microsimulation
import numpy as np
from policyengine_us import Microsimulation
import pandas as pd
from .process_puf import FINANCIAL_SUBSET as FINANCIAL_VARIABLES
from typing import Tuple


def generate_model_variables(
    dataset: str, time_period: str = "2022", no_weight_adjustment: bool = False
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
    equivalisation = {}

    # We need to normalise the targets. Common regression targets are often 1e1 to 1e3 (this informs the scale of the learning rate).
    COUNT_HOUSEHOLDS = household_weights.sum().item()
    FINANCIAL_EQUIVALISATION = COUNT_HOUSEHOLDS
    POPULATION_EQUIVALISATION = COUNT_HOUSEHOLDS / 1e5

    is_filer = simulation.calculate("tax_unit_is_filer").values
    household_has_filers = (
        simulation.map_result(is_filer, "tax_unit", "household") > 0
    )

    for variable_name in FINANCIAL_VARIABLES:
        if variable_name not in parameters.gov.irs.soi:
            continue
        label = (
            simulation.tax_benefit_system.variables[variable_name].label
            + " (IRS SOI)"
        )
        values_df[label] = (
            simulation.calculate(variable_name, map_to="household").values
            * household_has_filers
        )
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
        label = (
            simulation.tax_benefit_system.variables[variable_name].label
            + " (CBO)"
        )
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

    demographics_sim = Microsimulation(dataset="cps_2022")

    # Total population
    values_df["U.S. population"] = simulation.calculate(
        "people", map_to="household"
    ).values
    targets["U.S. population"] = parameters.gov.census.populations.total
    equivalisation["U.S. population"] = POPULATION_EQUIVALISATION

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
            equivalisation[name] = POPULATION_EQUIVALISATION

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
            equivalisation[name] = POPULATION_EQUIVALISATION

    # Number of tax returns by AGI category

    # is_filer

    agi = simulation.calculate("adjusted_gross_income").values

    BOUNDS = [
        -np.inf,
        1,
        5e3,
        10e3,
        15e3,
        20e3,
        25e3,
        30e3,
        40e3,
        50e3,
        75e3,
        100e3,
        200e3,
        500e3,
        1e6,
        1.5e6,
        2e6,
        5e6,
        10e6,
        np.inf,
    ]
    COUNTS = [
        4_098_522,
        8_487_025,
        8_944_908,
        10_056_377,
        9_786_580,
        8_863_570,
        8_787_576,
        16_123_068,
        12_782_334,
        22_653_934,
        14_657_726,
        24_044_481,
        9_045_567,
        1_617_144,
        376_859,
        156_020,
        233_838,
        63_406,
        45_404,
    ]
    VALUES = [
        -171_836_364,
        19_987_243,
        67_651_359,
        125_912_056,
        170_836_129,
        199_508_960,
        241_347_179,
        561_386_434,
        573_155_378,
        1_392_395_599,
        1_271_699_391,
        3_297_058_075,
        2_619_188_471,
        1_092_599_034,
        454_552_875,
        268_278_123,
        698_923_219,
        435_242_550,
        1_477_728_359,
        13_879_929_368,
        -12_835_378,
        451_204,
        1_358_544,
        14_362_205,
        57_643_020,
        101_727_915,
        141_934_070,
        382_385_416,
        457_336_377,
        1_238_178_360,
        1_206_614_503,
        3_252_746_502,
        2_613_795_014,
        1_091_571_914,
        3_332_659_702,
    ]

    for i in range(len(BOUNDS) - 1):
        lower_bound = BOUNDS[i]
        upper_bound = BOUNDS[i + 1]
        in_range = (agi >= lower_bound) * (agi < upper_bound) * is_filer
        household_filers = simulation.map_result(
            in_range, "tax_unit", "household"
        )
        if lower_bound == -np.inf:
            lower_bound_str = "negative infinity"
        else:
            lower_bound_str = f"{lower_bound:,.0f}"
        name = f"tax returns with AGI between ${lower_bound_str} and ${upper_bound:,.0f}"
        values_df[name] = household_filers
        targets[name] = COUNTS[i] * population_growth_since_21
        equivalisation[name] = POPULATION_EQUIVALISATION

        agi_in_range = agi * in_range
        household_agi = simulation.map_result(
            agi_in_range, "tax_unit", "household"
        )
        name = f"total AGI from tax returns with AGI between ${lower_bound_str} and ${upper_bound:,.0f}"
        values_df[name] = household_agi
        targets[name] = VALUES[i] * population_growth_since_21 * 1e3
        equivalisation[name] = FINANCIAL_EQUIVALISATION

    # Tax return counts by filing status

    filing_status = (
        simulation.calculate("filing_status")
        .replace("SURVIVING_SPOUSE", "JOINT")
        .values
    )
    for filing_status_value in [
        "SINGLE",
        "JOINT",
        "HEAD_OF_HOUSEHOLD",
        "SEPARATE",
    ]:
        parameter = parameters.gov.irs.soi.returns_by_filing_status[
            filing_status_value
        ]
        in_filing_status = filing_status == filing_status_value
        household_filers = simulation.map_result(
            in_filing_status * is_filer, "tax_unit", "household"
        )
        labels = {
            "SINGLE": "single",
            "JOINT": "joint and widow(er)",
            "HEAD_OF_HOUSEHOLD": "head of household",
            "SEPARATE": "separate",
        }
        label = labels.get(filing_status_value) + " returns (IRS SOI)"
        values_df[label] = household_filers
        targets[label] = parameter
        equivalisation[label] = POPULATION_EQUIVALISATION

    targets_array = np.array(list(targets.values()))
    equivalisation_factors_array = np.array(list(equivalisation.values()))

    return (
        household_weights,
        weight_adjustment,
        values_df,
        targets,
        targets_array,
        equivalisation_factors_array,
    )


def aggregate_np(
    adjusted_weights: np.ndarray, values: pd.DataFrame
) -> np.ndarray:
    broadcasted_weights = adjusted_weights.reshape(-1, 1)
    weighted_values = np.matmul(broadcasted_weights.T, values.values)
    return weighted_values


def get_snapshot(
    dataset: str,
    time_period: str = "2022",
) -> pd.DataFrame:
    """Returns a snapshot of the training metrics without training the model.

    Args:
        dataset (str): The name of the dataset to use.
        time_period (str, optional): The time period to use. Defaults to "2022".

    Returns:
        pd.DataFrame: A DataFrame containing the training metrics.
    """
    (
        household_weights,
        weight_adjustment,
        values_df,
        targets,
        targets_array,
        equivalisation_factors_array,
    ) = generate_model_variables(
        dataset, time_period, no_weight_adjustment=True
    )
    adjusted_weights = np.maximum(household_weights + weight_adjustment, 0)
    result = (
        aggregate_np(adjusted_weights, values_df)
        / equivalisation_factors_array
    )
    target = targets_array / equivalisation_factors_array
    current_aggregates = (result * equivalisation_factors_array)[0]
    loss = np.mean(((result / target - 1) ** 2) * np.log2(np.abs(target)))
    current_loss = loss.item()
    return pd.DataFrame(
        {
            "name": list(targets.keys()) + ["total"],
            "value": list(current_aggregates) + [current_loss],
            "target": list(targets.values()) + [0],
            "time_period": time_period,
        }
    )
