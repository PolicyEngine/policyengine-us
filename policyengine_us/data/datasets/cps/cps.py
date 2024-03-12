import logging
from policyengine_core.data import Dataset
from policyengine_us.data.storage import STORAGE_FOLDER
import h5py
from policyengine_us.data.datasets.cps.raw_cps import (
    RawCPS_2018,
    RawCPS_2019,
    RawCPS_2020,
    RawCPS_2021,
    RawCPS_2022,
    RawCPS,
)
from policyengine_us.data.datasets.cps.uprated_cps import UpratedCPS
from policyengine_us.data.storage import STORAGE_FOLDER
from pandas import DataFrame, Series
import numpy as np
import pandas as pd
import os
import yaml
from typing import Type


class CPS(Dataset):
    name = "cps"
    label = "CPS"
    raw_cps: Type[RawCPS] = None
    previous_year_raw_cps: Type[RawCPS] = None
    data_format = Dataset.ARRAYS

    def generate(self):
        """Generates the Current Population Survey dataset for PolicyEngine US microsimulations.
        Technical documentation and codebook here: https://www2.census.gov/programs-surveys/cps/techdocs/cpsmar21.pdf
        """

        raw_data = self.raw_cps(require=True).load()
        cps = h5py.File(self.file_path, mode="w")

        ENTITIES = ("person", "tax_unit", "family", "spm_unit", "household")
        person, tax_unit, family, spm_unit, household = [
            raw_data[entity] for entity in ENTITIES
        ]

        add_id_variables(cps, person, tax_unit, family, spm_unit, household)
        add_personal_variables(cps, person)
        add_personal_income_variables(cps, person, self.raw_cps.time_period)
        add_previous_year_income(self, cps)
        add_spm_variables(cps, spm_unit)
        add_household_variables(cps, household)

        raw_data.close()
        cps.close()

        cps = h5py.File(self.file_path, mode="a")
        cps.close()


def add_silver_plan_cost(self, cps: h5py.File, year: int):
    """Adds the second-lowest silver plan cost for each tax unit, based on geography.

    Args:
        cps (h5py.File): The CPS dataset file.
        year (int): The year of the data.
    """
    from policyengine_us import Microsimulation

    sim = Microsimulation(dataset=self)
    slspc = sim.calc("second_lowest_silver_plan_cost", year).values

    cps["second_lowest_silver_plan_cost"] = slspc


def add_id_variables(
    cps: h5py.File,
    person: DataFrame,
    tax_unit: DataFrame,
    family: DataFrame,
    spm_unit: DataFrame,
    household: DataFrame,
) -> None:
    """Add basic ID and weight variables.

    Args:
        cps (h5py.File): The CPS dataset file.
        person (DataFrame): The person table of the ASEC.
        tax_unit (DataFrame): The tax unit table created from the person table
            of the ASEC.
        family (DataFrame): The family table of the ASEC.
        spm_unit (DataFrame): The SPM unit table created from the person table
            of the ASEC.
        household (DataFrame): The household table of the ASEC.
    """
    # Add primary and foreign keys
    cps["person_id"] = person.PH_SEQ * 100 + person.P_SEQ
    cps["family_id"] = family.FH_SEQ * 10 + family.FFPOS
    cps["household_id"] = household.H_SEQ
    cps["person_tax_unit_id"] = person.TAX_ID
    cps["person_spm_unit_id"] = person.SPM_ID
    cps["tax_unit_id"] = tax_unit.TAX_ID
    cps["spm_unit_id"] = spm_unit.SPM_ID
    cps["person_household_id"] = person.PH_SEQ
    cps["person_family_id"] = person.PH_SEQ * 10 + person.PF_SEQ

    # Add weights
    # Weights are multiplied by 100 to avoid decimals
    cps["person_weight"] = person.A_FNLWGT / 1e2
    cps["family_weight"] = family.FSUP_WGT / 1e2

    # Tax unit weight is the weight of the containing family.
    family_weight = Series(
        cps["family_weight"][...], index=cps["family_id"][...]
    )
    person_family_id = cps["person_family_id"][...]
    persons_family_weight = Series(family_weight[person_family_id])
    cps["tax_unit_weight"] = persons_family_weight.groupby(
        cps["person_tax_unit_id"][...]
    ).first()

    cps["spm_unit_weight"] = spm_unit.SPM_WEIGHT / 1e2

    cps["household_weight"] = household.HSUP_WGT / 1e2

    # Marital units

    marital_unit_id = person.PH_SEQ * 1e6 + np.maximum(
        person.A_LINENO, person.A_SPOUSE
    )

    # marital_unit_id is not the household ID, zero padded and followed
    # by the index within household (of each person, or their spouse if
    # one exists earlier in the survey).

    marital_unit_id = Series(marital_unit_id).rank(
        method="dense"
    )  # Simplify to a natural number sequence with repetitions [0, 1, 1, 2, 3, ...]

    cps["person_marital_unit_id"] = marital_unit_id.values
    cps["marital_unit_id"] = marital_unit_id.drop_duplicates().values


def add_personal_variables(cps: h5py.File, person: DataFrame) -> None:
    """Add personal demographic variables.

    Args:
        cps (h5py.File): The CPS dataset file.
        person (DataFrame): The CPS person table.
    """

    # The CPS provides age as follows:
    # 00-79 = 0-79 years of age
    # 80 = 80-84 years of age
    # 85 = 85+ years of age
    # We assign the 80 ages randomly between 80 and 84.
    # to avoid unrealistically bunching at 80.
    cps["age"] = np.where(
        person.A_AGE == 80,
        # NB: randint is inclusive of first argument, exclusive of second.
        np.random.randint(80, 85, len(person)),
        person.A_AGE,
    )
    # A_SEX is 1 -> male, 2 -> female.
    cps["is_female"] = person.A_SEX == 2
    # "Is...blind or does...have serious difficulty seeing even when Wearing
    #  glasses?" 1 -> Yes
    cps["is_blind"] = person.PEDISEYE == 1
    DISABILITY_FLAGS = [
        "PEDIS" + i for i in ["DRS", "EAR", "EYE", "OUT", "PHY", "REM"]
    ]
    cps["is_disabled"] = (person[DISABILITY_FLAGS] == 1).any(axis=1)

    def children_per_parent(col: str) -> pd.DataFrame:
        """Calculate number of children in the household using parental
            pointers.

        Args:
            col (str): Either PEPAR1 and PEPAR2, which correspond to A_LINENO
            of the person's first and second parent in the household,
            respectively.
        """
        return (
            person[person[col] > 0]
            .groupby(["PH_SEQ", col])
            .size()
            .reset_index()
            .rename(columns={col: "A_LINENO", 0: "children"})
        )

    # Aggregate to parent.
    res = (
        pd.concat(
            [children_per_parent("PEPAR1"), children_per_parent("PEPAR2")]
        )
        .groupby(["PH_SEQ", "A_LINENO"])
        .children.sum()
        .reset_index()
    )
    tmp = person[["PH_SEQ", "A_LINENO"]].merge(
        res, on=["PH_SEQ", "A_LINENO"], how="left"
    )
    cps["own_children_in_household"] = tmp.children.fillna(0)

    cps["has_marketplace_health_coverage"] = person.MRK == 1

    cps["cps_race"] = person.PRDTRACE
    cps["is_hispanic"] = person.PRDTHSP != 0

    cps["is_widowed"] = person.A_MARITL == 4
    cps["is_separated"] = person.A_MARITL == 6


def add_personal_income_variables(
    cps: h5py.File, person: DataFrame, year: int
):
    """Add income variables.

    Args:
        cps (h5py.File): The CPS dataset file.
        person (DataFrame): The CPS person table.
        year (int): The CPS year
    """
    # Get income imputation parameters.
    yamlfilename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "imputation_parameters.yaml",
    )
    with open(yamlfilename, "r", encoding="utf-8") as yamlfile:
        p = yaml.safe_load(yamlfile)
    assert isinstance(p, dict)

    # Assign CPS variables.
    cps["employment_income"] = person.WSAL_VAL
    cps["taxable_interest_income"] = person.INT_VAL * (
        p["taxable_interest_fraction"]
    )
    cps["tax_exempt_interest_income"] = person.INT_VAL * (
        1 - p["taxable_interest_fraction"]
    )
    cps["self_employment_income"] = person.SEMP_VAL
    cps["farm_income"] = person.FRSE_VAL
    cps["qualified_dividend_income"] = person.DIV_VAL * (
        p["qualified_dividend_fraction"]
    )
    cps["non_qualified_dividend_income"] = person.DIV_VAL * (
        1 - p["qualified_dividend_fraction"]
    )
    cps["rental_income"] = person.RNT_VAL
    # Assign Social Security retirement benefits if at least 62.
    MINIMUM_RETIREMENT_AGE = 62
    cps["social_security_retirement"] = np.where(
        person.A_AGE >= MINIMUM_RETIREMENT_AGE, person.SS_VAL, 0
    )
    # Otherwise assign them to Social Security disability benefits.
    cps["social_security_disability"] = (
        person.SS_VAL - cps["social_security_retirement"]
    )
    # Provide placeholders for other Social Security inputs to avoid creating
    # NaNs as they're uprated.
    cps["social_security_dependents"] = np.zeros_like(
        cps["social_security_retirement"]
    )
    cps["social_security_survivors"] = np.zeros_like(
        cps["social_security_retirement"]
    )
    cps["unemployment_compensation"] = person.UC_VAL
    # Add pensions and annuities.
    cps_pensions = person.PNSN_VAL + person.ANN_VAL
    # Assume a constant fraction of pension income is taxable.
    cps["taxable_private_pension_income"] = (
        cps_pensions * p["taxable_pension_fraction"]
    )
    cps["tax_exempt_private_pension_income"] = cps_pensions * (
        1 - p["taxable_pension_fraction"]
    )
    # Retirement account distributions.
    RETIREMENT_CODES = {
        1: "401k",
        2: "403b",
        3: "roth_ira",
        4: "regular_ira",
        5: "keogh",
        6: "sep",  # Simplified Employee Pension plan
        7: "other_type_retirement_account",
    }
    for code, description in RETIREMENT_CODES.items():
        tmp = 0
        # The ASEC splits distributions across four variable pairs.
        for i in ["1", "2", "1_YNG", "2_YNG"]:
            tmp += (person["DST_SC" + i] == code) * person["DST_VAL" + i]
        cps[f"{description}_distributions"] = tmp
    # Allocate retirement distributions by taxability.
    for source_with_taxable_fraction in ["401k", "403b", "sep"]:
        cps[f"taxable_{source_with_taxable_fraction}_distributions"] = (
            cps[f"{source_with_taxable_fraction}_distributions"][...]
            * p[
                f"taxable_{source_with_taxable_fraction}_distribution_fraction"
            ]
        )
        cps[f"tax_exempt_{source_with_taxable_fraction}_distributions"] = cps[
            f"{source_with_taxable_fraction}_distributions"
        ][...] * (
            1
            - p[
                f"taxable_{source_with_taxable_fraction}_distribution_fraction"
            ]
        )
        del cps[f"{source_with_taxable_fraction}_distributions"]

    # Assume all regular IRA distributions are taxable,
    # and all Roth IRA distributions are not.
    cps["taxable_ira_distributions"] = cps["regular_ira_distributions"]
    cps["tax_exempt_ira_distributions"] = cps["roth_ira_distributions"]
    # Other income (OI_VAL) is a catch-all for all other income sources.
    # The code for alimony income is 20.
    cps["alimony_income"] = (person.OI_OFF == 20) * person.OI_VAL
    # The code for strike benefits is 12.
    cps["strike_benefits"] = (person.OI_OFF == 12) * person.OI_VAL
    cps["child_support_received"] = person.CSP_VAL
    # Assume all public assistance / welfare dollars (PAW_VAL) are TANF.
    # They could also include General Assistance.
    cps["tanf_reported"] = person.PAW_VAL
    cps["ssi_reported"] = person.SSI_VAL
    # Assume all retirement contributions are traditional 401(k) for now.
    # Procedure for allocating retirement contributions:
    # 1) If they report any self-employment income, allocate entirely to
    #    self-employed pension contributions.
    # 2) If they report any wage and salary income, allocate in this order:
    #    a) Traditional 401(k) contributions up to to limit
    #    b) Roth 401(k) contributions up to the limit
    #    c) IRA contributions up to the limit, split according to administrative fractions
    #    d) Other retirement contributions
    # Disregard reported pension contributions from people who report neither wage and salary
    # nor self-employment income.
    # Assume no 403(b) or 457 contributions for now.
    LIMIT_401K_2022 = 20_500
    LIMIT_401K_CATCH_UP_2022 = 6_500
    LIMIT_IRA_2022 = 6_000
    LIMIT_IRA_CATCH_UP_2022 = 1_000
    CATCH_UP_AGE_2022 = 50
    retirement_contributions = person.RETCB_VAL
    cps["self_employed_pension_contributions"] = np.where(
        person.SEMP_VAL > 0, retirement_contributions, 0
    )
    remaining_retirement_contributions = np.maximum(
        retirement_contributions - cps["self_employed_pension_contributions"],
        0,
    )
    # Compute the 401(k) limit for the person's age.
    catch_up_eligible = person.A_AGE >= CATCH_UP_AGE_2022
    limit_401k = LIMIT_401K_2022 + catch_up_eligible * LIMIT_401K_CATCH_UP_2022
    limit_ira = LIMIT_IRA_2022 + catch_up_eligible * LIMIT_IRA_CATCH_UP_2022
    cps["traditional_401k_contributions"] = np.where(
        person.WSAL_VAL > 0,
        np.minimum(remaining_retirement_contributions, limit_401k),
        0,
    )
    remaining_retirement_contributions = np.maximum(
        remaining_retirement_contributions
        - cps["traditional_401k_contributions"],
        0,
    )
    cps["roth_401k_contributions"] = np.where(
        person.WSAL_VAL > 0,
        np.minimum(remaining_retirement_contributions, limit_401k),
        0,
    )
    remaining_retirement_contributions = np.maximum(
        remaining_retirement_contributions - cps["roth_401k_contributions"],
        0,
    )
    cps["traditional_ira_contributions"] = np.where(
        person.WSAL_VAL > 0,
        np.minimum(remaining_retirement_contributions, limit_ira),
        0,
    )
    remaining_retirement_contributions = np.maximum(
        remaining_retirement_contributions
        - cps["traditional_ira_contributions"],
        0,
    )
    roth_ira_limit = limit_ira - cps["traditional_ira_contributions"]
    cps["roth_ira_contributions"] = np.where(
        person.WSAL_VAL > 0,
        np.minimum(remaining_retirement_contributions, roth_ira_limit),
        0,
    )
    # Allocate capital gains into long-term and short-term based on aggregate split.
    cps["long_term_capital_gains"] = person.CAP_VAL * (
        p["long_term_capgain_fraction"]
    )
    cps["short_term_capital_gains"] = person.CAP_VAL * (
        1 - p["long_term_capgain_fraction"]
    )
    cps["receives_wic"] = person.WICYN == 1
    cps["veterans_benefits"] = person.VET_VAL
    cps["workers_compensation"] = person.WC_VAL
    # Disability income has multiple sources and values split across two pairs
    # of variables. Include everything except for worker's compensation
    # (code 1), which is defined as WC_VAL.
    WORKERS_COMP_DISABILITY_CODE = 1
    disability_benefits_1 = person.DIS_VAL1 * (
        person.DIS_SC1 != WORKERS_COMP_DISABILITY_CODE
    )
    disability_benefits_2 = person.DIS_VAL2 * (
        person.DIS_SC2 != WORKERS_COMP_DISABILITY_CODE
    )
    cps["disability_benefits"] = disability_benefits_1 + disability_benefits_2
    # Expenses.
    # "What is the annual amount of child support paid?"
    cps["child_support_expense"] = person.CHSP_VAL
    cps["health_insurance_premiums"] = person.PHIP_VAL
    cps["medical_out_of_pocket_expenses"] = person.MOOP


def add_spm_variables(cps: h5py.File, spm_unit: DataFrame) -> None:
    SPM_RENAMES = dict(
        spm_unit_total_income_reported="SPM_TOTVAL",
        snap_reported="SPM_SNAPSUB",
        spm_unit_capped_housing_subsidy_reported="SPM_CAPHOUSESUB",
        free_school_meals_reported="SPM_SCHLUNCH",
        spm_unit_energy_subsidy_reported="SPM_ENGVAL",
        spm_unit_wic_reported="SPM_WICVAL",
        spm_unit_broadband_subsidy_reported="SPM_BBSUBVAL",
        spm_unit_payroll_tax_reported="SPM_FICA",
        spm_unit_federal_tax_reported="SPM_FEDTAX",
        # State tax includes refundable credits.
        spm_unit_state_tax_reported="SPM_STTAX",
        spm_unit_capped_work_childcare_expenses="SPM_CAPWKCCXPNS",
        spm_unit_medical_expenses="SPM_MEDXPNS",
        spm_unit_spm_threshold="SPM_POVTHRESHOLD",
        spm_unit_net_income_reported="SPM_RESOURCES",
        spm_unit_pre_subsidy_childcare_expenses="SPM_CHILDCAREXPNS",
    )

    for openfisca_variable, asec_variable in SPM_RENAMES.items():
        if asec_variable in spm_unit.columns:
            cps[openfisca_variable] = spm_unit[asec_variable]

    cps["reduced_price_school_meals_reported"] = (
        cps["free_school_meals_reported"][...] * 0
    )


def add_household_variables(cps: h5py.File, household: DataFrame) -> None:
    cps["state_fips"] = household.GESTFIPS
    cps["county_fips"] = household.GTCO
    state_county_fips = cps["state_fips"][...] * 1e3 + cps["county_fips"][...]
    # Assign is_nyc here instead of as a variable formula so that it shows up
    # as toggleable in the webapp.
    # List county FIPS codes for each NYC county/borough.
    NYC_COUNTY_FIPS = [
        5,  # Bronx
        47,  # Kings (Brooklyn)
        61,  # New York (Manhattan)
        81,  # Queens
        85,  # Richmond (Staten Island)
    ]
    # Compute NYC by concatenating NY state FIPS with county FIPS.
    # For example, 36061 is Manhattan.
    NYS_FIPS = 36
    nyc_full_county_fips = [
        NYS_FIPS * 1e3 + county_fips for county_fips in NYC_COUNTY_FIPS
    ]
    cps["in_nyc"] = np.isin(state_county_fips, nyc_full_county_fips)


def add_previous_year_income(self, cps: h5py.File) -> None:
    if self.previous_year_raw_cps is None:
        print(
            "No previous year data available for this dataset, skipping previous year income imputation."
        )
        return

    from survey_enhance.impute import Imputation

    cps_current_year_data = self.raw_cps(require=True).load()
    cps_previous_year_data = self.previous_year_raw_cps(require=True).load()
    cps_previous_year = cps_previous_year_data.person.set_index(
        cps_previous_year_data.person.PERIDNUM
    )
    cps_current_year = cps_current_year_data.person.set_index(
        cps_current_year_data.person.PERIDNUM
    )

    previous_year_data = cps_previous_year[
        ["WSAL_VAL", "SEMP_VAL", "I_ERNVAL", "I_SEVAL"]
    ].rename(
        {
            "WSAL_VAL": "employment_income_last_year",
            "SEMP_VAL": "self_employment_income_last_year",
        },
        axis=1,
    )

    previous_year_data = previous_year_data[
        (previous_year_data.I_ERNVAL == 0) & (previous_year_data.I_SEVAL == 0)
    ]

    previous_year_data.drop(["I_ERNVAL", "I_SEVAL"], axis=1, inplace=True)

    joined_data = cps_current_year.join(previous_year_data)[
        [
            "employment_income_last_year",
            "self_employment_income_last_year",
            "I_ERNVAL",
            "I_SEVAL",
        ]
    ]
    joined_data["previous_year_income_available"] = (
        ~joined_data.employment_income_last_year.isna()
        & ~joined_data.self_employment_income_last_year.isna()
        & (joined_data.I_ERNVAL == 0)
        & (joined_data.I_SEVAL == 0)
    )
    joined_data = joined_data.fillna(-1).drop(["I_ERNVAL", "I_SEVAL"], axis=1)

    # CPS already ordered by PERIDNUM, so the join wouldn't change the order.
    cps["employment_income_last_year"] = joined_data[
        "employment_income_last_year"
    ].values
    cps["self_employment_income_last_year"] = joined_data[
        "self_employment_income_last_year"
    ].values
    cps["previous_year_income_available"] = joined_data[
        "previous_year_income_available"
    ].values


class CPS_2019(CPS):
    name = "cps_2019"
    label = "CPS 2019"
    raw_cps = RawCPS_2019
    previous_year_raw_cps = RawCPS_2018
    file_path = STORAGE_FOLDER / "cps_2019.h5"
    time_period = 2019


class CPS_2020(CPS):
    name = "cps_2020"
    label = "CPS 2020"
    raw_cps = RawCPS_2020
    file_path = STORAGE_FOLDER / "cps_2020.h5"
    time_period = 2020


class CPS_2021(CPS):
    name = "cps_2021"
    label = "CPS 2021"
    raw_cps = RawCPS_2021
    file_path = STORAGE_FOLDER / "cps_2021.h5"
    time_period = 2021


class CPS_2022(CPS):
    name = "cps_2022"
    label = "CPS 2022"
    raw_cps = RawCPS_2022
    previous_year_raw_cps = RawCPS_2021
    file_path = STORAGE_FOLDER / "cps_2022.h5"
    time_period = 2022


CPS_2023 = UpratedCPS.from_dataset(
    CPS_2022,
    2023,
    "cps_2023",
    "CPS 2023",
    STORAGE_FOLDER / "cps_2023.h5",
    new_url="release://policyengine/policyengine-us/cps-2023/cps_2023.h5",
)
