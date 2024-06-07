import pandas as pd
from microdf import MicroDataFrame
from survey_enhance import Imputation
from typing import Tuple
import numpy as np

PUF_FILE_PATH = "~/Downloads/puf_2015.csv"
PUF_DEMOGRAPHICS_FILE_PATH = "~/Downloads/demographics_2015.csv"


FILING_STATUS_MAP = {
    "SINGLE": 1,
    "JOINT": 2,
    "SEPARATE": 3,
    "HEAD_OF_HOUSEHOLD": 4,
    "SURVIVING_SPOUSE": 5,
}

# This update statement describes the demographic supplement.
DEMOGRAPHICS_CODEBOOK = {
    "AGEDP1": "age_dependent_1",
    "AGEDP2": "age_dependent_2",
    "AGEDP3": "age_dependent_3",
    "AGERANGE": "age_range_primary_filer",
    "EARNSPLIT": "earnings_split_joint_returns",
    "GENDER": "gender_primary_filer",
    "RECID": "return_id",
}

CPS_DATASET = "cps_2022"

DEMOGRAPHIC_VARIABLES = [
    "age_dependent_1",
    "age_dependent_2",
    "age_dependent_3",
    "age_range_primary_filer",
    "earnings_split_joint_returns",
    "gender_primary_filer",
]

NON_FINANCIAL_COLUMNS = [
    "return_id",
    "tax_unit_weight",
]

FINANCIAL_SUBSET = [
    "alimony_expense",
    "alimony_income",
    "casualty_loss",
    "cdcc_relevant_expenses",
    "charitable_cash_donations",
    "charitable_non_cash_donations",
    "domestic_production_ald",
    "early_withdrawal_penalty",
    "educator_expense",
    "employment_income",
    "estate_income",
    "farm_income",
    "farm_rent_income",
    "health_savings_account_ald",
    "interest_deduction",
    "long_term_capital_gains",
    "long_term_capital_gains_on_collectibles",
    "medical_expense",
    "non_qualified_dividend_income",
    "partnership_s_corp_income",
    "qualified_dividend_income",
    "qualified_tuition_expenses",
    "real_estate_taxes",
    "rental_income",
    "self_employment_income",
    "self_employed_health_insurance_ald",
    "self_employed_pension_contribution_ald",
    "short_term_capital_gains",
    "social_security",
    "state_income_tax_reported",
    "student_loan_interest",
    "taxable_interest_income",
    "taxable_pension_income",
    "taxable_unemployment_compensation",
    "taxable_ira_distributions",
    "tax_exempt_interest_income",
    "tax_exempt_pension_income",
    "traditional_ira_contributions",
    "unrecaptured_section_1250_gain",
]


def load_puf(
    puf_file_path: str = None, puf_demographics_path: str = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load the PUF and demographics data.

    Returns:
        puf (pd.DataFrame): The PUF data.
        puf_with_demographics (pd.DataFrame): The subset of the PUF data that has demographic information.
    """
    if puf_file_path is None:
        puf_file_path = "~/Downloads/puf_2015.csv"
    if puf_demographics_path is None:
        puf_demographics_path = "~/Downloads/demographics_2015.csv"
    puf = pd.read_csv(puf_file_path).fillna(0)
    demographics = pd.read_csv(puf_demographics_path).fillna(0)

    demographics = demographics.dropna()

    puf.S006 = puf.S006 / 100

    df = pd.DataFrame()

    df["alimony_expense"] = puf.E03500
    df["alimony_income"] = puf.E00800
    df["casualty_loss"] = puf.E20500
    df["cdcc_relevant_expenses"] = puf.E32800
    df["charitable_cash_donations"] = puf.E19800
    df["charitable_non_cash_donations"] = puf.E20100
    df["count_exemptions"] = puf.XTOT
    df["domestic_production_ald"] = puf.E03240
    df["early_withdrawal_penalty"] = puf.E03400
    df["educator_expense"] = puf.E03220
    df["employment_income"] = puf.E00200
    df["estate_income"] = puf.E26390 - puf.E26400
    df["farm_income"] = puf.T27800
    df["farm_rent_income"] = puf.E27200
    df["health_savings_account_ald"] = puf.E03290
    df["interest_deduction"] = puf.E19200
    df["long_term_capital_gains"] = puf.P23250
    df["long_term_capital_gains_on_collectibles"] = puf.E24518
    df["medical_expense"] = puf.E17500
    df["non_qualified_dividend_income"] = puf.E00600 - puf.E00650
    df["partnership_s_corp_income"] = np.maximum(puf.E26270, 0)
    df["qualified_dividend_income"] = puf.E00650
    df["qualified_tuition_expenses"] = puf.E03230
    df["real_estate_taxes"] = puf.E18500
    df["rental_income"] = puf.E25850 - puf.E25860
    df["self_employment_income"] = puf.E00900
    df["self_employed_health_insurance_ald"] = puf.E03270
    df["self_employed_pension_contribution_ald"] = puf.E03300
    df["short_term_capital_gains"] = puf.P22250
    df["social_security"] = puf.E02400
    df["state_income_tax_reported"] = puf.E18400
    df["student_loan_interest"] = puf.E03210
    df["taxable_interest_income"] = puf.E00300
    df["taxable_pension_income"] = puf.E01700
    df["taxable_unemployment_compensation"] = puf.E02300
    df["taxable_ira_distributions"] = puf.E01400
    df["tax_exempt_interest_income"] = puf.E00400
    df["tax_exempt_pension_income"] = puf.E01500 - puf.E01700
    df["traditional_ira_contributions"] = puf.E03150
    df["unrecaptured_section_1250_gain"] = puf.E24515

    df["filing_status"] = puf.MARS.map(
        {
            0: "SINGLE",  # Assume the aggregate record is single
            1: "SINGLE",
            2: "JOINT",
            3: "SEPARATE",
            4: "HEAD_OF_HOUSEHOLD",
        }
    )
    df["return_id"] = puf.RECID
    df["tax_unit_weight"] = puf.S006

    puf = df

    demographics = demographics.rename(columns=DEMOGRAPHICS_CODEBOOK)

    return puf, demographics


def uprate_puf(puf: pd.DataFrame, time_period: str) -> pd.DataFrame:
    from policyengine_us.system import system

    gov = system.parameters.calibration.gov
    soi = gov.irs.soi

    # Uprate the financial subset

    for variable_name in FINANCIAL_SUBSET:
        if variable_name not in soi.children:
            uprater = gov.cbo.income_by_source.adjusted_gross_income
        else:
            uprater = soi.children[variable_name]
        value_in_2015 = uprater("2015-01-01")
        value_now = uprater(f"{time_period}-01-01")
        uprating_factor = value_now / value_in_2015
        puf[variable_name] = puf[variable_name] * uprating_factor

    return puf


def impute_missing_demographics(
    puf: pd.DataFrame,
    demographics: pd.DataFrame,
) -> pd.DataFrame:
    """Impute missing demographic information from the PUF.

    Args:
        puf (pd.DataFrame): The PUF data.
        puf_with_demographics (pd.DataFrame): The subset of the PUF data that has demographic information.

    Returns:
        puf_with_imputed_demographics (pd.DataFrame): The PUF data with imputed demographic information.
    """


    puf.filing_status = puf.filing_status.map(
        FILING_STATUS_MAP
    )

    demographics_from_puf = Imputation()
    puf_with_demographics = (
        puf[puf.return_id.isin(demographics.return_id)]
        .merge(demographics, on="return_id")
        .fillna(0)
    )

    demographics_from_puf.train(
        puf_with_demographics.drop(columns=DEMOGRAPHIC_VARIABLES),
        puf_with_demographics[DEMOGRAPHIC_VARIABLES],
    )

    puf_without_demographics = puf[
        ~puf.return_id.isin(puf_with_demographics.return_id)
    ].reset_index()
    predicted_demographics = demographics_from_puf.predict(
        puf_without_demographics
    )
    puf_with_imputed_demographics = pd.concat(
        [puf_without_demographics, predicted_demographics], axis=1
    )

    weighted_puf_with_demographics = MicroDataFrame(
        puf_with_demographics, weights="tax_unit_weight"
    )
    weighted_puf_with_imputed_demographics = MicroDataFrame(
        puf_with_imputed_demographics, weights="tax_unit_weight"
    )

    puf_combined = pd.concat(
        [
            weighted_puf_with_demographics,
            weighted_puf_with_imputed_demographics,
        ]
    )

    puf_combined.filing_status = puf_combined.filing_status.map(
        {value: key for key, value in FILING_STATUS_MAP.items()}
    )

    return puf_combined


def generate_puf_style_cps(time_period: str) -> pd.DataFrame:
    """Generate a PUF-style table from the CPS.

    Returns:
        cps (pd.DataFrame): The CPS data.
    """
    from policyengine_us import Microsimulation

    sim = Microsimulation(dataset=f"cps_{time_period}")

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
    filing_status = sim.calculate("filing_status").replace("SURVIVING_SPOUSE", "JOINT")

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
    cps_demographics["filing_status"] = filing_status
    return pd.DataFrame(cps_demographics)


def impute_puf_financials_to_cps(
    cps_demographics: pd.DataFrame,
    puf: pd.DataFrame,
):
    """Impute PUF financials to the CPS.

    Args:
        cps_demographics (pd.DataFrame): The CPS data with demographic information.
        puf (pd.DataFrame): The PUF data.

    Returns:
        cps_imputed (pd.DataFrame): The CPS data with imputed financial information.
    """
    puf.filing_status = puf.filing_status.map(FILING_STATUS_MAP)
    income_from_demographics = Imputation()

    puf_X = puf[DEMOGRAPHIC_VARIABLES + ["filing_status"]]
    puf_y = puf[FINANCIAL_SUBSET]

    income_from_demographics.train(
        puf_X,
        puf_y,
        sample_weight=puf["tax_unit_weight"],
    )
    cps_demographics.filing_status = cps_demographics.filing_status.map(FILING_STATUS_MAP)

    cps_X = cps_demographics[DEMOGRAPHIC_VARIABLES + ["filing_status"]]

    cps_financial_predictions = income_from_demographics.predict(
        cps_X
    )
    cps_imputed = pd.concat(
        [cps_demographics, cps_financial_predictions], axis=1
    )
    cps_imputed = MicroDataFrame(
        cps_imputed, weights=cps_demographics.tax_unit_weight
    )

    cps_imputed.filing_status = cps_imputed.filing_status.map({
        value: key for key, value in FILING_STATUS_MAP.items()
    })

    return cps_imputed


def project_tax_unit_cps_to_person_level(
    puf_style_cps: pd.DataFrame, time_period: str
) -> pd.DataFrame:
    from policyengine_us import Microsimulation

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
    time_period: str = "2022",
) -> pd.DataFrame:
    """Generate a PUF-imputed CPS at the person level.

    Args:
        verbose (bool): Whether to print progress statements.
        time_period (str): The time period to uprate the PUF to.

    Returns:
        person_level_puf_imputed_cps (pd.DataFrame): The PUF-imputed CPS at the person level.
    """
    if verbose:
        print("Loading PUF and demographics")
    puf, demographics = load_puf()

    puf = uprate_puf(puf, time_period)

    if verbose:
        print("Imputing missing demographics")
    puf = impute_missing_demographics(puf, demographics)

    if verbose:
        print("Generating PUF-style CPS")
    puf_style_cps = generate_puf_style_cps(time_period)

    if verbose:
        print("Imputing PUF financials to CPS")
    puf_imputed_cps = impute_puf_financials_to_cps(puf_style_cps, puf)

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
