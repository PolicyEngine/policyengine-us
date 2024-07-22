import pandas as pd
import numpy as np
from policyengine_us.data.storage import STORAGE_FOLDER

ITMDED_GROW_RATE = 0.02  # annual growth rate in itemized deduction amounts

USE_VARIABLE_SPECIFIC_POPULATION_GROWTH_DIVISORS = False

SOI_TO_PUF_STRAIGHT_RENAMES = {
    "employment_income": "E00200",
    "capital_gains_distributions": "E01100",
    # CG gains and lossses targeted separately
    "taxable_interest_income": "E00300",
    "exempt_interest": "E00400",
    "ordinary_dividends": "E00600",
    "qualified_dividends": "E00650",
    # Business income profits and losses targeted separately
    # QBI deduction not in 2015 PUF
    "ira_distributions": "E01400",
    "total_pension_income": "E01500",
    "taxable_pension_income": "E01700",
    # Partnership and S-corp income targeted separately
    "unemployment_compensation": "E02300",
    "total_social_security": "E02400",
    "taxable_social_security": "E02500",
    "medical_expense_deductions_uncapped": "E17500",
    # "state_and_local_tax_deductions": "E18400",
    "itemized_state_income_tax_deductions": "E18400",
    "itemized_real_estate_tax_deductions": "E18500",
    "interest_paid_deductions": "E19200",
    "charitable_contributions_deductions": "E19800",
}

SOI_TO_PUF_POS_ONLY_RENAMES = {
    "business_net_profits": "E00900",
    "capital_gains_gross": "E01000",
    "partnership_and_s_corp_income": "E26270",
}
SOI_TO_PUF_NEG_ONLY_RENAMES = {
    "business_net_losses": "E00900",
    "capital_gains_losses": "E01000",
    "partnership_and_s_corp_losses": "E26270",
}

REMAINING_VARIABLES = [
    "E03500",
    "E00800",
    "E20500",
    "E32800",
    "E20100",
    "E03240",
    "E03400",
    "E03220",
    "E26390",
    "E26400",
    "T27800",
    "E27200",
    "E03290",
    "P23250",
    "E24518",
    "E20400",
    "E26270",
    "E03230",
    "E25850",
    "E25860",
    "E00900",
    "E03270",
    "E03300",
    "P22250",
    "E03210",
    "E03150",
    "E24515",
    "E07300",
    "E62900",
    "E01200",
    "E00700",
    "E58990",
    "E07400",
    "E07600",
    "E11200",
    "E87521",
    "E07260",
    "E09900",
    "P08000",
    "E07240",
    "E09700",
    "E09800",
]

soi = pd.read_csv(STORAGE_FOLDER / "soi.csv")


def get_soi_aggregate(variable, year, is_count):
    if variable == "adjusted_gross_income" and is_count:
        # AGI isn't treated like the other variables
        return get_soi_aggregate("count", year, True)

    is_variable = soi.Variable == variable
    is_year = soi.Year == year
    filing_status = soi["Filing status"] == "All"
    agi_lower = soi["AGI lower bound"] == -np.inf
    agi_upper = soi["AGI upper bound"] == np.inf
    count_status = soi["Count"] == is_count
    non_taxable_only = soi["Taxable only"] == False

    return (
        soi[
            is_variable
            & is_year
            & filing_status
            & agi_lower
            & agi_upper
            & count_status
            & non_taxable_only
        ]
        .iloc[0]
        .Value
    )


def get_growth(variable, from_year, to_year):
    start_value = get_soi_aggregate(variable, from_year, False)
    end_value = get_soi_aggregate(variable, to_year, False)

    if USE_VARIABLE_SPECIFIC_POPULATION_GROWTH_DIVISORS:
        start_population = get_soi_aggregate(variable, from_year, True)
        end_population = get_soi_aggregate(variable, to_year, True)
    else:
        start_population = get_soi_aggregate("count", from_year, True)
        end_population = get_soi_aggregate("count", to_year, True)

    aggregate_growth = end_value / start_value
    population_growth = end_population / start_population

    return aggregate_growth / population_growth


def uprate_puf(puf, from_year, to_year):
    print(f"Uprating PUF from {from_year} to {to_year}...")
    puf = puf.copy()
    for variable in SOI_TO_PUF_STRAIGHT_RENAMES:
        growth = get_growth(variable, from_year, to_year)
        if variable in [
            "medical_expense_deductions_uncapped",
            "itemized_state_income_tax_deductions",
            "itemized_real_estate_tax_deductions",
            "interest_paid_deductions",
            "charitable_contributions_deductions",
        ]:
            # print("%% OLD_VAR_GROWTH:", variable, growth)
            nyears = to_year - from_year
            growth = (1.0 + ITMDED_GROW_RATE) ** nyears
            # print("%% NEW_VAR_GROWTH:", variable, growth)
        puf[SOI_TO_PUF_STRAIGHT_RENAMES[variable]] *= growth

    # Positive and negative split variables
    for variable in SOI_TO_PUF_POS_ONLY_RENAMES:
        growth = get_growth(variable, from_year, to_year)
        puf_variable = SOI_TO_PUF_POS_ONLY_RENAMES[variable]
        puf[puf_variable][puf[puf_variable] > 0] *= growth

    for variable in SOI_TO_PUF_NEG_ONLY_RENAMES:
        growth = get_growth(variable, from_year, to_year)
        puf_variable = SOI_TO_PUF_NEG_ONLY_RENAMES[variable]
        puf[puf_variable][puf[puf_variable] < 0] *= growth

    # Remaining variables, uprate purely by AGI growth
    # (for now, because I'm not sure how to handle the deductions,
    #  credits, and incomes separately)
    for variable in REMAINING_VARIABLES:
        growth = get_growth("adjusted_gross_income", from_year, to_year)
        puf[variable] *= growth

    # Uprate the weights
    returns_start = get_soi_aggregate("count", from_year, True)
    returns_end = get_soi_aggregate("count", to_year, True)
    puf.S006 *= returns_end / returns_start

    return puf
