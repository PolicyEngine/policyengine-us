import torch
import pandas as pd
import numpy as np
from policyengine_us import Microsimulation
import plotly.express as px
from tqdm import tqdm

simulation = Microsimulation()
TIME_PERIOD = 2023
simulation.default_calculation_period = TIME_PERIOD
parameters = simulation.tax_benefit_system.parameters.calibration(
    f"{TIME_PERIOD}-01-01"
)

household_weights = torch.tensor(
    simulation.calculate("household_weight").values, dtype=torch.float32
)
weight_adjustment = torch.tensor(
    np.random.random(household_weights.shape) * 0,
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
    "above_the_line_deductions",
]

for variable_name in AGI_VARIABLES:
    values_df[variable_name] = simulation.calculate(
        variable_name, map_to="household"
    ).values
    targets[variable_name] = parameters.gov.cbo.income_by_source[variable_name]
    equivalisation[variable_name] = FINANCIAL_EQUIVALISATION

# Payroll taxes
values_df["payroll_taxes"] = (
    simulation.calculate("employee_payroll_tax", map_to="household").values
    + simulation.calculate("self_employment_tax", map_to="household").values
)
targets["payroll_taxes"] = parameters.gov.cbo.payroll_taxes
equivalisation["payroll_taxes"] = FINANCIAL_EQUIVALISATION

# Program spending from CBO baseline projections

PROGRAMS = [
    "income_tax",
    "snap",
    "social_security",
    "ssi",
    "unemployment_compensation",
]

for variable_name in PROGRAMS:
    values_df[variable_name] = simulation.calculate(
        variable_name, map_to="household"
    ).values
    targets[variable_name] = parameters.gov.cbo[variable_name]
    equivalisation[variable_name] = FINANCIAL_EQUIVALISATION

# EITC tax expenditure
values_df["eitc"] = simulation.calculate("eitc", map_to="household").values
targets["eitc"] = parameters.gov.treasury.tax_expenditures.eitc
equivalisation["eitc"] = FINANCIAL_EQUIVALISATION

# Total population
values_df["population"] = simulation.calculate(
    "people", map_to="household"
).values
targets["population"] = parameters.populations.total
equivalisation["population"] = POPULATION_EQUIVALISATION

# Population by 5-year age group and sex
age = simulation.calculate("age").values
is_male = simulation.calculate("is_male")
for lower_age_group in range(0, 90, 5):
    for possible_is_male in (True, False):
        in_age_range = (age >= lower_age_group) & (age < lower_age_group + 5)
        in_sex_category = is_male == possible_is_male
        count_people_in_range = simulation.map_result(
            in_age_range * in_sex_category, "person", "household"
        )
        sex_category = "male" if possible_is_male else "female"
        name = f"population_{lower_age_group}_to_{lower_age_group + 5}_{sex_category}"
        values_df[name] = count_people_in_range
        targets[name] = (household_weights.numpy() * count_people_in_range).sum()
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
        name = f"population_adults_{count_adults}_children_{count_children}"
        values_df[name] = in_criteria
        targets[name] = (household_weights.numpy() * in_criteria).sum()
        equivalisation[name] = POPULATION_EQUIVALISATION

# Tax filing unit counts by filing status

filing_status = simulation.calculate("filing_status").values

for filing_status_value in np.unique(filing_status):
    is_filing_status = filing_status == filing_status_value
    name = f"population_filing_status_{filing_status_value}"
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

progress_bar = tqdm(range(10_000), desc="Calibrating weights")
for i in progress_bar:
    adjusted_weights = torch.relu(household_weights + weight_adjustment)
    result = (
        aggregate(adjusted_weights, values_df) / equivalisation_factors_array
    )
    loss = torch.sum(
        (result - targets_array / equivalisation_factors_array) ** 2
    )
    loss.backward()
    if i % 50 == 0:
        current_loss = loss.item()
        progress_bar.set_description_str(
            f"Calibrating weights | Loss = {current_loss:,.0f}"
        )
        current_aggregates = (
            (result * equivalisation_factors_array).detach().numpy()[0]
        )
        training_log_df = training_log_df.append(
            pd.DataFrame(
                {
                    "name": list(targets.keys()),
                    "epoch": [i] * len(targets),
                    "value": list(current_aggregates),
                    "target": list(targets.values()),
                }
            )
        )
    weight_adjustment.data -= 1e-2 * weight_adjustment.grad
    weight_adjustment.grad.zero_()

training_log_df.to_csv("training_log.csv.gz", compression="gzip")
