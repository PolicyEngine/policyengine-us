from openfisca_us.microdata import CE


def test_ce_from_2019():
    """Test the Consumer Expenditure data generating functions for 2019

    Note that the assertions are based on estimates done prior to integration
    into the openfisca-us-data package and do not exactly match published
    Consumer Expenditure values. However, only the interview data was used for
    these estimates (not the diary data) and the documentation warns that
    users may not be able to match published values due to data disclosure
    limitations. These were considered sufficiently close for the purposes
    of simulation.
    """
    # 2019 Constants, calculated from the CE ---------------------------------
    INCOME_BEFORE_TAX_2019_PRECOMPUTED = 82743
    ALCOHOL_2019_PRECOMPUTED = 536
    CU_CO2_EMISSIONS_2019_PRECOMPUTED = 26903

    # Emissions constants ----------------------------------------------------
    HHS_IN_US_2019 = 122.8e6  # Source: 2019 ACS, presented by Google Search
    KG_PER_METRIC_TON = 1000

    # Generate and load the CE data ------------------------------------------
    CE.generate(2019)
    ce_2019 = CE.load(2019)

    # Test top level of HDF5 hierarchy ---------------------------------------
    assert len(set(ce_2019.keys()).intersection({"annual", "household"})) == 2

    # Test household average demographic estimate ----------------------------
    est_income_bf_tax = ce_2019["/annual/income_before_tax"][()]
    assert round(est_income_bf_tax) == INCOME_BEFORE_TAX_2019_PRECOMPUTED

    # Test household average expenditure estimate ----------------------------
    est_alcohol_expense = ce_2019["/annual/alcohol"][()]
    assert round(est_alcohol_expense) == ALCOHOL_2019_PRECOMPUTED

    # Test Household Sector CO2 emissions are "in the ballpark" --------------
    est_co2_kg_per_cu = ce_2019["/annual/co2_kg"][()]
    est_total_tons_co2 = est_co2_kg_per_cu * HHS_IN_US_2019 / KG_PER_METRIC_TON
    assert round(est_total_tons_co2 / 1e9) > 2
    assert round(est_total_tons_co2 / 1e9) < 6

    # Test Household Sector CO2 emissions only need to be "in the ballpark" --
    hh_keys = {"demographics", "emissions", "expenditures", "survey"}
    assert len(set(ce_2019["/household"].keys()).intersection(hh_keys)) == 4

    hh_co2_emissions = ce_2019["/household/emissions/co2_kg"][:]
    assert len(hh_co2_emissions) == CU_CO2_EMISSIONS_2019_PRECOMPUTED
