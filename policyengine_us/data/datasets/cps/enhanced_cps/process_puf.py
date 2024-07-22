import pandas as pd
from microdf import MicroDataFrame
from survey_enhance import Imputation
from typing import Tuple
from policyengine_us.system import system
from policyengine_us import Microsimulation
from policyengine_us.data.datasets.cps.cps import CPS_2021
from policyengine_us.data.datasets.puf.puf import (
    PUF_2021,
    FINANCIAL_SUBSET,
    PUF_FILE_PATH,
    PUF_DEMOGRAPHICS_FILE_PATH,
)
import numpy as np


def generate_puf_style_dataset(dataset) -> pd.DataFrame:
    """Generate a PUF-style table from a PolicyEngine hierarchical dataset.

    Returns:
        cps (pd.DataFrame): The CPS data.
    """

    sim = Microsimulation(dataset=dataset)

    cps_demographics = pd.DataFrame(index=sim.calculate("tax_unit_id").values)

    df = sim.calculate_dataframe(
        ["age", "tax_unit_id", "is_tax_unit_dependent"]
    )
    df = df[df.is_tax_unit_dependent]
    df_sorted = df.sort_values(["tax_unit_id", "age"])
    df_sorted["rank"] = df_sorted.groupby("tax_unit_id")["age"].rank()

    df_sorted["age_dependent_1"] = np.where(
        df_sorted["rank"] == 1, df_sorted["age"], -1
    )
    df_sorted["age_dependent_2"] = np.where(
        df_sorted["rank"] == 2, df_sorted["age"], -1
    )
    df_sorted["age_dependent_3"] = np.where(
        df_sorted["rank"] == 3, df_sorted["age"], -1
    )

    df_sorted_maxed = df_sorted.groupby("tax_unit_id").max()

    cps_demographics["age_dependent_1"] = df_sorted_maxed["age_dependent_1"]
    cps_demographics["age_dependent_2"] = df_sorted_maxed["age_dependent_2"]
    cps_demographics["age_dependent_3"] = df_sorted_maxed["age_dependent_3"]

    cps_demographics = cps_demographics.fillna(-1)

    # Define the age bins and labels
    bins = [-np.inf, -1, 4, 12, 16, 18, 23, np.inf]
    labels = [0, 1, 2, 3, 4, 5, 6]

    # Create AGEDP1, AGEDP2, AGEDP3 based on the categories
    for col in ["age_dependent_1", "age_dependent_2", "age_dependent_3"]:
        cps_demographics[col] = pd.cut(
            cps_demographics[col], bins=bins, labels=labels, right=True
        )

    cps_demographics.reset_index(inplace=True)
    cps_demographics = cps_demographics[
        ["age_dependent_1", "age_dependent_2", "age_dependent_3"]
    ]

    cps_demographics["age_range_primary_filer"] = sim.calculate(
        "age_head"
    ).values

    bins_head = [-np.inf, -1, 25, 34, 44, 54, 64, np.inf]
    labels_head = [0, 1, 2, 3, 4, 5, 6]

    cps_demographics["age_range_primary_filer"] = pd.cut(
        cps_demographics["age_range_primary_filer"],
        bins=bins_head,
        labels=labels_head,
        right=True,
    )

    is_male = sim.calculate("is_male")
    is_head = sim.calculate("is_tax_unit_head")
    male_head = sim.map_result(is_male * is_head, "person", "tax_unit")
    tax_unit_filer_gender = np.where(male_head, 1, 2)

    cps_demographics["gender_primary_filer"] = tax_unit_filer_gender

    filer_earned = sim.calculate("head_earned")
    spouse_earned = sim.calculate("spouse_earned")
    filing_status = sim.calculate("filing_status")

    def determine_earning_split_value(
        filer: float, spouse: float, filing_status: str
    ) -> int:
        if filing_status != "JOINT":
            return 0
        if filer + spouse <= 0:
            return 1
        ratio_filer = filer / (filer + spouse)
        if ratio_filer >= 0.75:
            return 1
        elif ratio_filer >= 0.25:
            return 2
        else:
            return 3

    cps_demographics["earnings_split_joint_returns"] = np.vectorize(
        determine_earning_split_value
    )(filer_earned, spouse_earned, filing_status)
    cps_demographics["tax_unit_weight"] = sim.calculate(
        "tax_unit_weight"
    ).values
    return pd.DataFrame(cps_demographics)


DEMOGRAPHIC_VARIABLES = [
    # Demographic variables to use for imputation
    "age_range_primary_filer",
    "gender_primary_filer",
    "age_dependent_1",
    "age_dependent_2",
    "age_dependent_3",
    "earnings_split_joint_returns",
]


def impute_puf_financials_to_cps(
    cps_demographics: pd.DataFrame,
    puf_dataset: str,
):
    """Impute PUF financials to the CPS.

    Args:
        cps_demographics (pd.DataFrame): The CPS data with demographic information.
        puf (pd.DataFrame): The PUF data.

    Returns:
        cps_imputed (pd.DataFrame): The CPS data with imputed financial information.
    """

    puf_demographics = generate_puf_style_dataset(puf_dataset)
    puf_values = Microsimulation(dataset=puf_dataset).calculate_dataframe(
        FINANCIAL_SUBSET,
        map_to="tax_unit",
    )
    puf = pd.concat([puf_demographics, puf_values], axis=1)

    income_from_demographics = Imputation()

    income_from_demographics.train(
        puf[DEMOGRAPHIC_VARIABLES],
        puf[FINANCIAL_SUBSET],
        sample_weight=puf.household_weight,
    )

    cps_financial_predictions = income_from_demographics.predict(
        cps_demographics[DEMOGRAPHIC_VARIABLES],
        mean_quantile=0.5,
    )
    cps_imputed = pd.concat(
        [cps_demographics, cps_financial_predictions], axis=1
    )
    cps_imputed = MicroDataFrame(
        cps_imputed, weights=cps_demographics.tax_unit_weight
    )

    return cps_imputed


def project_tax_unit_cps_to_person_level(
    puf_style_cps: pd.DataFrame, time_period: str
) -> pd.DataFrame:
    """Project tax unit CPS to person level.

    Args:
        puf_style_cps (pd.DataFrame): The CPS data with imputed financial information.

    Returns:
        person_df (pd.DataFrame): The CPS data with imputed financial information projected to the person level.
    """
    sim = Microsimulation(dataset=f"cps_{time_period}")
    person_df = pd.DataFrame(
        dict(
            person_id=sim.calculate("person_id").values,
            tax_unit_id=sim.calculate("person_tax_unit_id").values,
        )
    )

    tax_unit_df = pd.DataFrame(
        dict(
            tax_unit_id=sim.calculate("tax_unit_id").values,
        ),
    )

    person_is_tax_filer_head = sim.calculate("is_tax_unit_head").values

    for variable in FINANCIAL_SUBSET:
        if sim.tax_benefit_system.variables[variable].entity.key == "tax_unit":
            tax_unit_df[variable] = puf_style_cps[variable].values
        else:
            cps_original_value = sim.calculate(variable).values
            cps_tax_unit_original_total = sim.map_result(
                sim.map_result(cps_original_value, "person", "tax_unit"),
                "tax_unit",
                "person",
            )
            cps_share_of_tax_unit_original_total = (
                cps_original_value / cps_tax_unit_original_total
            )
            cps_share_of_tax_unit_original_total = np.where(
                np.isnan(cps_share_of_tax_unit_original_total),
                person_is_tax_filer_head,
                cps_share_of_tax_unit_original_total,
            )
            mapped_down_imputed_values = sim.map_result(
                puf_style_cps[variable].values, "tax_unit", "person"
            )
            person_df[variable] = (
                cps_share_of_tax_unit_original_total
                * mapped_down_imputed_values
            )

    person_df = person_df.fillna(0)
    tax_unit_df = tax_unit_df.fillna(0)
    return person_df, tax_unit_df


def puf_imputed_cps_person_level(
    verbose: bool = True,
    time_period: str = 2021,
) -> pd.DataFrame:
    """Generate a PUF-imputed CPS at the person level.

    Args:
        verbose (bool): Whether to print progress statements.
        time_period (str): The time period to uprate the PUF to.

    Returns:
        person_level_puf_imputed_cps (pd.DataFrame): The PUF-imputed CPS at the person level.
    """

    if verbose:
        print("Generating PUF-style CPS")
    puf_style_cps = generate_puf_style_dataset(CPS_2021)

    if verbose:
        print("Imputing PUF financials to CPS")
    puf_imputed_cps = impute_puf_financials_to_cps(puf_style_cps, PUF_2021)

    if verbose:
        print("Projecting tax unit CPS to person level")
    (
        person_level_puf_imputed_cps,
        tax_unit_level_puf_imputed_cps,
    ) = project_tax_unit_cps_to_person_level(
        puf_imputed_cps,
        time_period,
    )

    if verbose:
        print("Done")
    return person_level_puf_imputed_cps, tax_unit_level_puf_imputed_cps


if __name__ == "__main__":
    puf_imputed_cps_person_level(verbose=True)
