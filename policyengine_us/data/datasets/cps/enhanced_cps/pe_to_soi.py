import pandas as pd
import numpy as np
from tqdm import tqdm
from tax_microdata_benchmarking.storage import STORAGE_FOLDER
import warnings

warnings.filterwarnings("ignore")

soi = pd.read_csv(STORAGE_FOLDER / "input" / "soi.csv")


def pe_to_soi(pe_dataset, year):
    from policyengine_us import Microsimulation

    pe_sim = Microsimulation(dataset=pe_dataset)
    df = pd.DataFrame()

    pe = lambda variable: np.array(
        pe_sim.calculate(variable, map_to="tax_unit")
    )

    df["adjusted_gross_income"] = pe("adjusted_gross_income")
    df["exemption"] = pe("exemptions")
    df["itemded"] = pe("itemized_taxable_income_deductions")
    df["income_tax_after_credits"] = pe("income_tax")
    df["total_income_tax"] = pe("income_tax_before_credits")
    df["taxable_income"] = pe("taxable_income")
    df["business_net_profits"] = pe("self_employment_income") * (
        pe("self_employment_income") > 0
    )
    df["business_net_losses"] = -pe("self_employment_income") * (
        pe("self_employment_income") < 0
    )
    df["capital_gains_distributions"] = pe("non_sch_d_capital_gains")
    df["capital_gains_gross"] = pe("loss_limited_net_capital_gains") * (
        pe("loss_limited_net_capital_gains") > 0
    )
    df["capital_gains_losses"] = -pe("loss_limited_net_capital_gains") * (
        pe("loss_limited_net_capital_gains") < 0
    )
    df["estate_income"] = pe("estate_income") * (pe("estate_income") > 0)
    df["estate_losses"] = -pe("estate_income") * (pe("estate_income") < 0)
    df["exempt_interest"] = pe("tax_exempt_interest_income")
    df["ira_distributions"] = pe("taxable_ira_distributions")
    df["count_of_exemptions"] = pe("exemptions_count")
    df["ordinary_dividends"] = pe("non_qualified_dividend_income") + pe(
        "qualified_dividend_income"
    )
    df["partnership_and_s_corp_income"] = pe("partnership_s_corp_income") * (
        pe("partnership_s_corp_income") > 0
    )
    df["partnership_and_s_corp_losses"] = -pe("partnership_s_corp_income") * (
        pe("partnership_s_corp_income") < 0
    )
    df["total_pension_income"] = pe("pension_income")
    df["taxable_pension_income"] = pe("taxable_pension_income")
    df["qualified_dividends"] = pe("qualified_dividend_income")
    df["rent_and_royalty_net_income"] = pe("rental_income") * (
        pe("rental_income") > 0
    )
    df["rent_and_royalty_net_losses"] = -pe("rental_income") * (
        pe("rental_income") < 0
    )
    df["total_social_security"] = pe("social_security")
    df["taxable_social_security"] = pe("taxable_social_security")
    df["income_tax_before_credits"] = pe("income_tax_before_credits")
    df["taxable_interest_income"] = pe("taxable_interest_income")
    df["unemployment_compensation"] = pe("taxable_unemployment_compensation")
    df["employment_income"] = pe("irs_employment_income")
    df["qualified_business_income_deduction"] = pe(
        "qualified_business_income_deduction"
    )
    df["charitable_contributions_deduction"] = pe("charitable_deduction")
    df["interest_paid_deductions"] = pe("interest_deduction")
    df["medical_expense_deductions_uncapped"] = pe("medical_expense_deduction")
    df["state_and_local_tax_deductions"] = pe("salt_deduction")
    df["itemized_state_income_and_sales_tax_deductions"] = pe(
        "state_and_local_sales_or_income_tax"
    )
    df["itemized_real_estate_tax_deductions"] = pe("real_estate_taxes")
    df["is_tax_filer"] = True
    df["count"] = 1

    df["filing_status"] = pe("filing_status")
    df["weight"] = pe("household_weight")
    df["household_id"] = pe("household_id")

    return df


def compare_soi_replication_to_soi(df, year):
    variables = []
    filing_statuses = []
    agi_lower_bounds = []
    agi_upper_bounds = []
    counts = []
    taxables = []
    full_pops = []
    values = []
    soi_values = []

    for i, row in soi.iterrows():
        if row.Year != year:
            continue

        if row.Variable not in df.columns:
            continue

        subset = df[df.adjusted_gross_income >= row["AGI lower bound"]][
            df.adjusted_gross_income < row["AGI upper bound"]
        ]

        variable = row["Variable"]

        fs = row["Filing status"]
        if fs == "Single":
            subset = subset[subset.filing_status == "SINGLE"]
        elif fs == "Head of Household":
            subset = subset[subset.filing_status == "HEAD_OF_HOUSEHOLD"]
        elif fs == "Married Filing Jointly/Surviving Spouse":
            subset = subset[subset.filing_status.isin(["JOINT", "WIDOW"])]
        elif fs == "Married Filing Separately":
            subset = subset[subset.filing_status == "SEPARATE"]

        if row["Taxable only"]:
            subset = subset[subset.total_income_tax > 0]
        else:
            subset = subset[subset.is_tax_filer]

        if row["Count"]:
            value = subset[subset[variable] > 0].weight.sum()
        else:
            value = (subset[variable] * subset.weight).sum()

        variables.append(row["Variable"])
        filing_statuses.append(row["Filing status"])
        agi_lower_bounds.append(row["AGI lower bound"])
        agi_upper_bounds.append(row["AGI upper bound"])
        counts.append(row["Count"] or (row["Variable"] == "count"))
        taxables.append(row["Taxable only"])
        full_pops.append(row["Full population"])
        values.append(value)
        soi_values.append(row["Value"])

    soi_replication = pd.DataFrame(
        {
            "Variable": variables,
            "Filing status": filing_statuses,
            "AGI lower bound": agi_lower_bounds,
            "AGI upper bound": agi_upper_bounds,
            "Count": counts,
            "Taxable only": taxables,
            "Full population": full_pops,
            "Value": values,
            "SOI Value": soi_values,
        }
    )

    soi_replication["Error"] = (
        soi_replication["Value"] - soi_replication["SOI Value"]
    )
    soi_replication["Absolute error"] = soi_replication["Error"].abs()
    soi_replication["Relative error"] = (
        (soi_replication["Error"] / soi_replication["SOI Value"])
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )
    soi_replication["Absolute relative error"] = soi_replication[
        "Relative error"
    ].abs()

    return soi_replication
