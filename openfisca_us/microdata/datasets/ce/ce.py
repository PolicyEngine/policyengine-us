import pkgutil

from pandas import DataFrame, concat
import numpy as np
import h5py
import yaml

from openfisca_us.microdata.utils import US, dataset
from openfisca_us.microdata.datasets.ce.raw_ce import RawCE


@dataset
class CE:
    """OpenFisca-US dataset for the Consumer Expenditure Survey

    The information extracted by RawCE and CE classes is from the "Interview
    Survey" (https://www.bls.gov/cex/pumd-getting-started-guide.htm#section3).
    Though there is also a "Diary Survey," the interview survey contains
    quarterly household level (technically "consumer unit") data deemed most
    appropriate for this project's needs. Only one set of files from the
    Interview Survey, called "FMLI" is used, and contains quarterly
    expenditures, annual income, assets, and liabilities, and household
    characteristics and survey weights.
    """

    name = "ce"
    model = US
    # Ratio of mean cash contributions to charity vs total cash contribs, 2016.
    # www.bls.gov/opub/btn/volume-8/the-relationship-between-cash-contributions-pretax-income-and-age.htm
    # Table 3. Average expenditures and cash contributions, by quintiles of
    #     pretax income, Consumer Expenditure Surveys, 2016.
    MEAN_CASH_CONTRIB_OUTSIDE_HOUSEHOLD_2016 = 2080.85
    MEAN_CASH_CONTRIB_TO_CHARITIES_2016 = 396.59
    proportion_cash_contrib_to_charity = (
        MEAN_CASH_CONTRIB_TO_CHARITIES_2016
        / MEAN_CASH_CONTRIB_OUTSIDE_HOUSEHOLD_2016
    )

    def generate(year: int) -> None:
        """Saves organized Consumer Expenditure data in HDF5 format via h5py

        Computes "months in scope" from existing variables and uses it to
        adjust weights and compute annual estimates. Those estimates
        are used to compute estimated carbon emissions per household.

        Args:
            year (int): The year of the Consumer Expenditure to use.
        """
        year = int(year)
        if year not in RawCE.years:
            RawCE.generate(year)

        raw_data = RawCE.load(year)
        ce = h5py.File(CE.file(year), mode="w")
        ce.create_group("/household")  # Household quarterly data.
        ce.create_group("/annual")  # Annual estimates.

        # Concatenate 5 "quarters" of fmli data, add months in scope. --------
        df_list = []
        for quarter_data in raw_data.keys():
            df_list.append(raw_data[quarter_data])

        fmli_df = concat(df_list)
        fmli_df["months_in_scope"] = fmli_df.apply(
            lambda row: months_in_scope(
                row["interview_mo"], row["nominal_quarter"]
            ),
            axis=1,
        )
        fmli_df = fmli_df.sort_values(["cu_id", "interview_id"])

        # Add household variables to H5 File. --------------------------------
        add_survey_vars(ce, fmli_df)
        add_demographics(ce, fmli_df)
        add_expenditures(ce, fmli_df)
        add_carbon_emissions(ce)

        # Add annual estimates to H5 File. -----------------------------------
        estimate_annual_quantity(
            ce, "/household/demographics/income_before_tax", "demographics"
        )
        estimate_annual_quantity(ce, "/household/expenditures/alcohol")
        estimate_annual_quantity(ce, "/household/emissions/co2_kg")
        raw_data.close()
        ce.close()


def months_in_scope(interview_mo: int, nominal_quarter: int):
    """Get the number of calendar months representing a nominal quarter.

    Args:
        interview_mo (int): the calendar month (e.g., 2 for February) that
            the Consumer Expenditure survey was taken
        nominal_quarter (int): The CE quarter of 1-5, with 5 representing the
            first quarter of the next year.

    Returns:
        months_in_scope (int): the number of calendar months (out of a
            possible 3) that will represent the nominal quarter.
    """
    if nominal_quarter in [1, 2, 3, 4]:
        if interview_mo in [1, 2, 3]:
            months_in_scope = interview_mo - 1
        elif interview_mo in [4, 5, 6, 7, 8, 9, 10, 11, 12]:
            months_in_scope = 3
        else:
            raise ValueError(f"interview_mo {interview_mo} outside range.")
    elif nominal_quarter == 5:
        if interview_mo in [1, 2, 3]:
            months_in_scope = 4 - interview_mo
        else:
            raise ValueError(f"interview_mo {interview_mo} outside range.")
    else:
        raise ValueError(f"nominal quarter {nominal_quarter} outside range.")
    return months_in_scope


def estimate_annual_quantity(ce: h5py.File, var_path: str, var_type="expense"):
    """Estimate an annual quantity using CE survey weights.

    When the var_type is "expense", months in scope of less than 3 will
        lead to proportionally scaled up values. Results are saved in
        "/annual."

    Args:
        ce (h5py.File): The HDF5 data structure containing the organized
           Consumer Expenditure survey data.
        var_path (str): the path within ce contining the survey variable
        var_type (str): either "expense" or "demographic".
    """
    if len(set(ce["/household/survey/nominal_year"][:])) > 1:
        raise NotImplementedError("Multi-year estimation not supported.")
    if var_type not in ["expense", "demographics"]:
        raise ValueError("var_type must be 'expense' or 'demographics'.")
    MONTHS_PER_QUARTER = 3
    nominal_quarter_ests = []
    for nominal_quarter in [1, 2, 3, 4, 5]:
        in_quarter = (
            ce["/household/survey/nominal_quarter"][:] == nominal_quarter
        )
        proportion_in_scope = (
            ce["/household/survey/months_in_scope"][in_quarter]
            / MONTHS_PER_QUARTER
        )
        weight = ce["/household/survey/weight"][in_quarter]
        var = ce[var_path][in_quarter]
        if var_type == "demographics":
            w = weight * proportion_in_scope
            numerator = np.sum(w * var)
            denominator = np.sum(w)
        elif var_type == "expense":
            numerator = np.sum(weight * var)
            denominator = np.sum(weight * proportion_in_scope)
        est = numerator / denominator
        nominal_quarter_ests.append(est)

        if var_type == "demographics":
            result = np.mean(nominal_quarter_ests)
        elif var_type == "expense":
            result = np.mean(nominal_quarter_ests) * 4

    estimated_name = var_path.split("/")[-1]
    ce["/annual/" + estimated_name] = result


def add_survey_vars(ce: h5py.File, fmli_df: DataFrame):
    """Add Consumer Expenditure variables related to the survey itself.

    Args:
        ce (h5py.File): The HDF5 data structure containing the organized
           Consumer Expenditure survey data.
        fmli_df (pd.DataFrame): The raw CE data (all 5 quarters).
    """
    group_prefix = "/household/survey/"
    ce[group_prefix + "weight"] = fmli_df["weight"]
    ce[group_prefix + "months_in_scope"] = fmli_df["months_in_scope"]
    ce[group_prefix + "nominal_year"] = fmli_df["nominal_year"]
    ce[group_prefix + "nominal_quarter"] = fmli_df["nominal_quarter"]
    ce[group_prefix + "interview_year"] = fmli_df["interview_yr"]
    ce[group_prefix + "interview_month"] = fmli_df["interview_mo"]
    ce[group_prefix + "survey_weight"] = fmli_df["FINLWT21"]


def add_demographics(ce: h5py.File, fmli_df: DataFrame):
    """Add select Consumer Expenditure demographic variables.

    Args:
        ce (h5py.File): The HDF5 data structure containing the organized
           Consumer Expenditure survey data.
        fmli_df (pd.DataFrame): The raw CE data (all 5 quarters).
    """
    group_prefix = "/household/demographics/"
    ce[group_prefix + "ref_age"] = fmli_df.AGE_REF
    ce[group_prefix + "ref_race"] = fmli_df.REF_RACE
    ce[group_prefix + "ref_sex"] = fmli_df.SEX_REF
    ce[group_prefix + "region"] = fmli_df.REGION
    ce[group_prefix + "state"] = fmli_df.STATE
    ce[group_prefix + "urban_or_rural"] = fmli_df.BLS_URBN
    ce[group_prefix + "census_division"] = fmli_df.DIVISION
    ce[group_prefix + "income_before_tax"] = fmli_df.FINCBTXM
    ce[group_prefix + "highest_education"] = fmli_df.HIGH_EDU
    ce[group_prefix + "members_ct"] = fmli_df.FAM_SIZE
    ce[group_prefix + "members_younger_than_18_ct"] = fmli_df.PERSLT18
    ce[group_prefix + "members_older_than_64_ct"] = fmli_df.PERSOT64


def add_expenditures(ce: h5py.File, fmli_df: DataFrame):
    """Add select Consumer Expenditure expenditure variables.

    Args:
        ce (h5py.File): The HDF5 data structure containing the organized
           Consumer Expenditure survey data.
        fmli_df (pd.DataFrame): The raw CE data (all 5 quarters).
    """
    group_prefix = "/household/expenditures/"
    ce[group_prefix + "airfare"] = fmli_df.TAIRFARP
    ce[group_prefix + "alcohol"] = fmli_df.ALCBEVPQ
    ce[group_prefix + "education"] = fmli_df.EDUCAPQ
    ce[group_prefix + "auto_insurance"] = fmli_df.VEHINSPQ
    ce[group_prefix + "autos"] = (
        fmli_df.CARTKUPQ  # used car.
        + fmli_df.CARTKNPQ  # new car.
        + fmli_df.VRNTLOPQ  # rent / lease.
    )
    ce[group_prefix + "books"] = fmli_df.READPQ
    ce[group_prefix + "charity"] = (
        fmli_df.CASHCOPQ * CE.proportion_cash_contrib_to_charity
    )
    ce[group_prefix + "clothes"] = fmli_df.APPARPQ
    ce[group_prefix + "electricity"] = fmli_df.ELCTRCPQ
    ce[group_prefix + "food_at_home"] = fmli_df.FDHOMEPQ
    ce[group_prefix + "food_at_restaurants"] = fmli_df.FDAWAYPQ
    ce[group_prefix + "furnishings"] = fmli_df.FURNTRPQ
    ce[group_prefix + "gasoline"] = fmli_df.GASMOPQ  # Inc motor oil.
    ce[group_prefix + "health"] = fmli_df.HEALTHPQ
    # Using "fuel oil" but another category includes "other fuels."
    ce[group_prefix + "home_heating_fuel"] = fmli_df.FULOILPQ
    ce[group_prefix + "household_supplies"] = fmli_df.OTHHEXPQ
    # Including personal insurance in this cateogry.
    ce[group_prefix + "life_insurance"] = fmli_df.LIFINSPQ
    ce[group_prefix + "mass_transit"] = fmli_df.PUBTRAPQ
    ce[group_prefix + "natural_gas"] = fmli_df.NTLGASPQ
    # "Other car services" is maintenance.
    ce[group_prefix + "other_car_services"] = fmli_df.MAINRPPQ
    # The word "other" is ignored
    ce[group_prefix + "other_dwelling_rentals"] = fmli_df.RENDWEPQ
    # judgement call here. Total outlays including sport equip.
    ce[group_prefix + "recreation_and_sports"] = fmli_df.EENTRMTP
    # OTHEQPPQ is part of total entertainment.
    ce[group_prefix + "other_recreation"] = fmli_df.OTHEQPPQ
    ce[group_prefix + "telephone"] = fmli_df.TELEPHPQ
    # tenant occupied dwellings is owned dwellings.
    ce[group_prefix + "tentant_occupied_dwellings"] = fmli_df.OWNDWEPQ
    ce[group_prefix + "tobacco"] = fmli_df.TOBACCPQ
    ce[group_prefix + "water"] = fmli_df.WATRPSPQ


def add_carbon_emissions(ce: h5py.File):
    """Add Carbon Emissions from Fremstad & Paul (2019)'s "extraction method."

    The paper is: Fremstad, Anders, and Mark Paul.
        "The impact of a carbon tax on inequality."
        Ecological Economics 163 (2019): 88-97.

    The table of coefficients is published in supplementary materials:
    docs.google.com/document/d/1jQlG1uz1UAPy6O_fmxyLQxRKLRDRpp5qmYdXKPXXXmM

    Args:
        ce (h5py.File): The HDF5 data structure containing the organized
           Consumer Expenditure survey data.
    """
    data = pkgutil.get_data(__name__, "emission_coefficients.yaml")
    emission_coefficients = yaml.load(data, Loader=yaml.FullLoader)
    group_prefix = "/household/expenditures/"
    ce["/household/emissions/co2_kg"] = sum(
        [
            emission_coefficients[category] * ce[group_prefix + category][:]
            for category in emission_coefficients.keys()
        ]
    )
