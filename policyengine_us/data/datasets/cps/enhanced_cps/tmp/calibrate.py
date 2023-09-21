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

person_df = pd.read_csv("puf_imputed_cps_person.csv.gz", compression="gzip")

FINANCIAL_VARIABLES = [
    "employment_income",
    "self_employment_income",
    "partnership_s_corp_income",
    "farm_income",
    "farm_rent_income",
    "short_term_capital_gains",
    "long_term_capital_gains",
    "taxable_interest_income",
    "tax_exempt_interest_income",
    "rental_income",
    "qualified_dividend_income",
    "non_qualified_dividend_income",
    "taxable_pension_income",
    "social_security",
]


class PUFExtendedCPS(Dataset):
    name = "puf_extended_cps"
    label = "PUF-extended CPS"
    file_path = "puf_extended_cps.h5"
    data_format = Dataset.ARRAYS
    time_period = "2023"

    def generate(self):
        new_data = {}
        cps = CPS_2023()
        cps_data = cps.load()
        for variable in list(set(cps.variables) | set(FINANCIAL_VARIABLES)):
            if "_id" in variable:
                # Append on a copy multiplied by 10
                new_data[variable] = np.concatenate(
                    [cps_data[variable][...], cps_data[variable][...] + 1e8]
                )
            elif "_weight" in variable:
                # Append on a zero-weighted copy
                new_data[variable] = np.concatenate(
                    [
                        cps_data[variable][...],
                        np.zeros_like(cps_data[variable][...]),
                    ]
                )
            else:
                # Append on a copy
                if variable in FINANCIAL_VARIABLES:
                    if variable not in cps.variables:
                        if variable == "social_security":
                            ## SS is an edge case
                            original_values = (
                                cps_data["social_security_retirement"][...]
                                + cps_data["social_security_disability"][...]
                            )
                        else:
                            original_values = np.zeros_like(
                                cps_data["employment_income"][...]
                            )
                    else:
                        original_values = cps_data[variable][...]
                    new_data[variable] = np.concatenate(
                        [original_values, person_df[variable].values]
                    )
                else:
                    new_data[variable] = np.concatenate(
                        [cps_data[variable][...], cps_data[variable][...]]
                    )

        self.save_dataset(new_data)


puf_extended_cps = PUFExtendedCPS()
puf_extended_cps.generate()


simulation = Microsimulation(dataset=puf_extended_cps)
TIME_PERIOD = 2023
simulation.default_calculation_period = TIME_PERIOD
parameters = simulation.tax_benefit_system.parameters.calibration(
    f"{TIME_PERIOD}-01-01"
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

# Financial totals
"""
AGI_VARIABLES = [
    "adjusted_gross_income",
    "employment_income",
    # "taxable_interest_and_ordinary_dividends", Doesn't exist yet
    "qualified_dividend_income",
    "net_capital_gain",
    "self_employment_income",
    "taxable_pension_income",
    "taxable_social_security",
    # "irs_other_income", Doesn't exist yet
    # "above_the_line_deductions",
]


for variable_name in AGI_VARIABLES:
    label = simulation.tax_benefit_system.variables[variable_name].label + " aggregate"
    values_df[label] = simulation.calculate(
        variable_name, map_to="household"
    ).values
    targets[label] = parameters.gov.cbo.income_by_source[variable_name]
    equivalisation[label] = FINANCIAL_EQUIVALISATION
"""

# Above is commented because we'll use IRS SOI aggregates uprated by CBO forecasts, rather than just CBO forecasts (SOI aggregates have more detail)

for variable_name in FINANCIAL_VARIABLES:
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
    entity_level = simulation.tax_benefit_system.variables[program].entity.key
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

    name = (
        f"Total AGI from tax returns with ${lower:,.0f} <= AGI < ${upper:,.0f}"
    )
    values_df[name] = household_agi_in_range
    targets[name] = agi_returns_values[i]
    equivalisation[name] = FINANCIAL_EQUIVALISATION

# Total population
values_df["U.S. population"] = simulation.calculate(
    "people", map_to="household"
).values
targets["U.S. population"] = parameters.populations.total
equivalisation["U.S. population"] = POPULATION_EQUIVALISATION

# Population by 10-year age group and sex
age = simulation.calculate("age").values
is_male = simulation.calculate("is_male")
for lower_age_group in range(0, 90, 10):
    for possible_is_male in (True, False):
        in_age_range = (age >= lower_age_group) & (age < lower_age_group + 5)
        in_sex_category = is_male == possible_is_male
        count_people_in_range = simulation.map_result(
            in_age_range * in_sex_category, "person", "household"
        )
        sex_category = "male" if possible_is_male else "female"
        name = f"{lower_age_group} to {lower_age_group + 5} and {sex_category} population"
        values_df[name] = count_people_in_range
        targets[name] = (
            household_weights.numpy() * count_people_in_range
        ).sum()
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
        targets[name] = (household_weights.numpy() * in_criteria).sum()
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
    ).sum()
    equivalisation[name] = POPULATION_EQUIVALISATION

targets_array = torch.tensor(list(targets.values()), dtype=torch.float32)
equivalisation_factors_array = torch.tensor(
    list(equivalisation.values()), dtype=torch.float32
)


def aggregate(
    adjusted_weights: torch.Tensor, values: pd.DataFrame
) -> torch.Tensor:
    broadcasted_weights = adjusted_weights.reshape(-1, 1)
    weighted_values = torch.matmul(
        broadcasted_weights.T, torch.tensor(values.values, dtype=torch.float32)
    )
    return weighted_values


training_log_df = pd.DataFrame()

progress_bar = tqdm(range(250_000), desc="Calibrating weights")
for i in progress_bar:
    adjusted_weights = torch.relu(household_weights + weight_adjustment)
    result = (
        aggregate(adjusted_weights, values_df) / equivalisation_factors_array
    )
    loss = torch.mean(
        (result - targets_array / equivalisation_factors_array) ** 2
    )
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
                    }
                ),
            ]
        )
    weight_adjustment.data -= 1e-1 * weight_adjustment.grad
    weight_adjustment.grad.zero_()

training_log_df.to_csv("training_log.csv.gz", compression="gzip")

from policyengine_us.data.storage import STORAGE_FOLDER


class EnhancedCPS(Dataset):
    name = "enhanced_cps"
    label = "Enhanced CPS"
    file_path = STORAGE_FOLDER / "enhanced_cps.h5"
    data_format = Dataset.ARRAYS
    time_period = "2023"

    def generate(self):
        new_data = {}
        cps = PUFExtendedCPS()
        cps_data = cps.load()
        for variable in cps.variables:
            if variable == "household_weight":
                new_data[variable] = adjusted_weights.detach().numpy()
            elif "_weight" not in variable:
                new_data[variable] = cps_data[variable][...]

        self.save_dataset(new_data)


enhanced_cps = EnhancedCPS()
enhanced_cps.generate()
