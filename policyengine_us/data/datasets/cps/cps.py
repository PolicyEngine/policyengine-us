import logging
from policyengine_core.data import PublicDataset
import h5py
from policyengine_us.data.datasets.cps.raw_cps import RawCPS
from policyengine_us.data.storage import policyengine_us_MICRODATA_FOLDER
from pandas import DataFrame, Series
import numpy as np
import pandas as pd
import os
import yaml


class CPS(PublicDataset):
    name = "cps"
    label = "CPS"
    model = "policyengine_us"
    folder_path = policyengine_us_MICRODATA_FOLDER

    url_by_year = {
        2020: "https://github.com/PolicyEngine/openfisca-us/releases/download/cps-v0/cps_2020.h5",
        2021: "https://github.com/PolicyEngine/policyengine-us/releases/download/cps-2021-v0/cps_2021.h5",
        2022: "https://github.com/PolicyEngine/policyengine-us/releases/download/cps-2021-v0/cps_2022.h5",
        2023: "https://github.com/PolicyEngine/policyengine-us/releases/download/cps-2021-v0/cps_2023.h5",
    }

    def generate(self, year: int):
        """Generates the Current Population Survey dataset for PolicyEngine US microsimulations.
        Technical documentation and codebook here: https://www2.census.gov/programs-surveys/cps/techdocs/cpsmar21.pdf

        Args:
            year (int): The year of the Raw CPS to use.
        """

        # Prepare raw CPS tables
        year = int(year)

        LATEST_YEAR = 2021

        if year > LATEST_YEAR:
            print(
                f"Currently, only the {LATEST_YEAR} ASEC is available. ",
                f"Uprating the {LATEST_YEAR} ASEC to {year}...",
            )
            if LATEST_YEAR not in CPS.years:
                print(
                    f"Didn't find the {LATEST_YEAR} CPS dataset. Generating..."
                )
                CPS.generate(LATEST_YEAR)

            from policyengine_us import Microsimulation

            sim = Microsimulation(dataset=CPS, dataset_year=LATEST_YEAR)
            uprated_cps = h5py.File(self.file(year), mode="w")
            latest_cps = h5py.File(self.file(LATEST_YEAR), mode="r")
            for variable in latest_cps:
                if variable in sim.tax_benefit_system.variables:
                    uprated_cps.create_dataset(
                        variable, data=sim.calculate(variable, year).values
                    )
            uprated_cps.close()
            latest_cps.close()
            return

        if year not in RawCPS.years:
            logging.info(f"Generating raw CPS for year {year}.")
            RawCPS.generate(year)

        raw_data = RawCPS.load(year)
        cps = h5py.File(self.file(year), mode="w")

        person, tax_unit, family, spm_unit, household = [
            raw_data[entity]
            for entity in (
                "person",
                "tax_unit",
                "family",
                "spm_unit",
                "household",
            )
        ]

        add_id_variables(cps, person, tax_unit, family, spm_unit, household)
        add_personal_variables(cps, person)
        add_personal_income_variables(cps, person, year)
        add_spm_variables(cps, spm_unit)
        add_household_variables(cps, household)

        raw_data.close()
        cps.close()

        cps = h5py.File(self.file(year), mode="a")
        add_silver_plan_cost(cps, year)
        cps.close()


def add_silver_plan_cost(cps: h5py.File, year: int):
    """Adds the second-lowest silver plan cost for each tax unit, based on geography.

    Args:
        cps (h5py.File): The CPS dataset file.
        year (int): The year of the data.
    """
    from policyengine_us import Microsimulation

    sim = Microsimulation(dataset=CPS, dataset_year=year)
    slspc = sim.calc("second_lowest_silver_plan_cost").values

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
    cps["is_ssi_disabled"] = (
        person[
            [
                "PEDISDRS",
                "PEDISEAR",
                "PEDISEYE",
                "PEDISOUT",
                "PEDISPHY",
                "PEDISREM",
            ]
        ].sum(axis=1)
        > 0
    )

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


def add_personal_income_variables(
    cps: h5py.File, person: DataFrame, year: int
):
    """Add income variables.

    Args:
        cps (h5py.File): The CPS dataset file.
        person (DataFrame): The CPS person table.
        year (int): The CPS year
    """
    # get income imputation parameters
    yamlfilename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "income_parameters.yaml"
    )
    with open(yamlfilename, "r", encoding="utf-8") as yamlfile:
        p = yaml.safe_load(yamlfile)
    assert isinstance(p, dict)

    # assign CPS variables
    cps["employment_income"] = person.WSAL_VAL
    cps["taxable_interest_income"] = person.INT_VAL * (
        p["taxable_interest_fraction"][year]
    )
    cps["tax_exempt_interest_income"] = person.INT_VAL * (
        1 - p["taxable_interest_fraction"][year]
    )
    cps["self_employment_income"] = person.SEMP_VAL
    cps["farm_income"] = person.FRSE_VAL
    cps["qualified_dividend_income"] = person.DIV_VAL * (
        p["qualified_dividend_fraction"][year]
    )
    cps["non_qualified_dividend_income"] = person.DIV_VAL * (
        1 - p["qualified_dividend_fraction"][year]
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
    cps["unemployment_compensation"] = person.UC_VAL
    cps_pensions = person.PNSN_VAL + person.ANN_VAL
    cps["taxable_pension_income"] = cps_pensions * (
        p["taxable_pension_fraction"][year]
    )
    cps["tax_exempt_pension_income"] = cps_pensions * (
        1 - p["taxable_pension_fraction"][year]
    )
    cps["alimony_income"] = (person.OI_OFF == 20) * person.OI_VAL
    cps["child_support_received"] = person.CSP_VAL
    cps["tanf_reported"] = person.PAW_VAL
    cps["ssi_reported"] = person.SSI_VAL
    cps["pension_contributions"] = person.RETCB_VAL
    cps["long_term_capital_gains"] = person.CAP_VAL * (
        p["long_term_capgain_fraction"][year]
    )
    cps["short_term_capital_gains"] = person.CAP_VAL * (
        1 - p["long_term_capgain_fraction"][year]
    )
    cps["receives_wic"] = person.WICYN == 1
    cps["veterans_benefits"] = person.VET_VAL
    # Expenses.
    # "What is the annual amount of child support paid?"
    person["child_support_expense"] = person.CHSP_VAL
    person["health_insurance_premiums"] = person.PHIP_VAL
    person["medical_out_of_pocket_expenses"] = person.MOOP


def add_spm_variables(cps: h5py.File, spm_unit: DataFrame) -> None:
    SPM_RENAMES = dict(
        spm_unit_total_income_reported="SPM_TOTVAL",
        snap_reported="SPM_SNAPSUB",
        spm_unit_capped_housing_subsidy_reported="SPM_CAPHOUSESUB",
        free_school_meals_reported="SPM_SCHLUNCH",
        spm_unit_energy_subsidy_reported="SPM_ENGVAL",
        spm_unit_wic_reported="SPM_WICVAL",
        spm_unit_payroll_tax_reported="SPM_FICA",
        spm_unit_federal_tax_reported="SPM_FEDTAX",
        spm_unit_state_tax_reported="SPM_STTAX",
        spm_unit_work_childcare_expenses="SPM_CAPWKCCXPNS",
        spm_unit_medical_expenses="SPM_MEDXPNS",
        spm_unit_spm_threshold="SPM_POVTHRESHOLD",
        spm_unit_net_income_reported="SPM_RESOURCES",
        childcare_expenses="SPM_CHILDCAREXPNS",
    )

    for openfisca_variable, asec_variable in SPM_RENAMES.items():
        cps[openfisca_variable] = spm_unit[asec_variable]

    cps["reduced_price_school_meals_reported"] = (
        cps["free_school_meals_reported"][...] * 0
    )


def add_household_variables(cps: h5py.File, household: DataFrame) -> None:
    cps["fips"] = household.GESTFIPS


CPS = CPS()
