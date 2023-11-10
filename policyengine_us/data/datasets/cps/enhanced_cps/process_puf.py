import pandas as pd
from microdf import MicroDataFrame
from survey_enhance import Imputation
from typing import Tuple
from policyengine_us.system import system
from policyengine_us import Microsimulation
import numpy as np

PUF_FILE_PATH = "~/Downloads/puf_2015.csv"
PUF_DEMOGRAPHICS_FILE_PATH = "~/Downloads/demographics_2015.csv"

codebook = {
    "E00200": "employment_income",
    "E00300": "interest_received",
    "E00400": "tax_exempt_interest_income",
    "E00600": "dividends_included_in_agi",
    "E00650": "qualified_dividend_income",
    "E00700": "state_income_tax_refunds",
    "E00800": "alimony_received",
    "E00900": "self_employment_income",
    "E01000": "net_capital_gain_loss",
    "E01100": "capital_gain_distributions",
    "E01200": "other_gains_loss",
    "E01400": "taxable_ira_distribution",
    "E01500": "total_pensions_annuities_received",
    "E01700": "taxable_pension_income",
    "E02000": "schedule_e_net_income_loss",
    "E02100": "schedule_f_net_profit_loss",
    "E02300": "unemployment_compensation_in_agi",
    "E02400": "social_security",
    "E02500": "social_security_benefits_in_agi",
    "E03150": "total_deductible_ira_payments",
    "E03210": "student_loan_interest_deduction",
    "E03220": "educator_expenses",
    "E03230": "tuition_fees_deduction",
    "E03260": "self_employment_tax_deduction",
    "E03270": "self_employed_health_insurance_deduction",
    "E03240": "domestic_production_activities_deduction",
    "E03290": "health_savings_account_deduction",
    "E03300": "payments_to_keogh_accounts",
    "E03400": "forfeited_interest_penalty",
    "E03500": "alimony_paid",
    "E00100": "adjusted_gross_income",
    "P04470": "total_deductions_standard_itemized",
    "E04600": "exemption_amount",
    "E04800": "taxable_income",
    "E05100": "tax_on_taxable_income",
    "E05200": "computed_regular_tax",
    "E05800": "income_tax_before_credits",
    "E06000": "income_subject_to_tax",
    "E06200": "marginal_tax_base",
    "E06300": "tax_generated_tax_rate_tables",
    "E09600": "alternative_minimum_tax",
    "E07180": "child_dependent_care_credit",
    "E07200": "elderly_disabled_credit",
    "E07220": "child_tax_credit",
    "E07230": "education_credits",
    "E07240": "retirement_savings_credit",
    "E07260": "residential_energy_credit",
    "E07300": "foreign_tax_credit",
    "E07400": "general_business_credit",
    "E07600": "credit_prior_year_minimum_tax",
    "P08000": "other_tax_credits",
    "E07150": "total_tax_credit_soi",
    "E06500": "total_income_tax",
    "E08800": "income_tax_after_credits_soi",
    "E09400": "self_employment_tax",
    "E09700": "recapture_taxes",
    "E09730": "total_additional_medicare_tax",
    "E09740": "net_investment_income_tax",
    "E09750": "health_care_individual_responsibility_payment",
    "E09800": "social_security_tax_tip_income",
    "E09900": "penalty_tax_ira",
    "E10300": "total_tax_liability_soi",
    "E10700": "income_tax_withheld",
    "E10900": "estimated_tax_payments",
    "E10960": "refundable_american_opportunity_credit",
    "E59560": "earned_income_eic",
    "E59680": "eic_offset_income_tax_before_credits",
    "E59700": "eic_offset_other_taxes_except_advance_eic",
    "E59720": "eic_refundable_portion",
    "E11550": "refundable_prior_year_minimum_tax_credit",
    "E11560": "net_premium_tax_credit",
    "E11561": "net_premium_tax_credit_offset_income_tax_before_credits",
    "E11562": "net_premium_tax_credit_offset_other_taxes",
    "E11563": "net_premium_tax_credit_refundable_portion",
    "E11070": "additional_child_tax_credit",
    "E11100": "amount_paid_form_4868_request_extension",
    "E11200": "excess_fica_rrta",
    "E11300": "credit_federal_tax_special_fuels_oils",
    "E11400": "regulated_investment_company_credit",
    "E11601": "total_refundable_credits_offset_income_tax_before_credits",
    "E11602": "total_refundable_credits_offset_other_taxes",
    "E11603": "total_refundable_credits_refundable_parts",
    "E10605": "total_tax_payments_soi",
    "E11900": "balance_due_overpayment",
    "E12000": "credit_elect",
    "E12200": "predetermined_estimated_tax_penalty",
    "E17500": "medical_dental_expenses_reduction_agi_limit",
    "E18400": "state_local_taxes",
    "E18500": "real_estate_tax_deductions",
    "E19200": "total_interest_paid_deduction",
    "E19550": "qualified_mortgage_insurance_premiums",
    "E19800": "cash_contributions",
    "E20100": "other_than_cash_contributions",
    "E19700": "contributions_deduction_total",
    "E20550": "unreimbursed_employee_business_expense",
    "E20600": "tax_preparation_fee",
    "E20400": "miscellaneous_deductions_agi_limitation_total",
    "E20800": "net_limited_miscellaneous_deductions",
    "E20500": "net_casualty_theft_loss",
    "E21040": "itemized_deduction_limitation",
    "P22250": "short_term_capital_gains",
    "E22320": "long_term_capital_gains_1",
    "E22370": "schedule_d_capital_gain_distributions",
    "P23250": "long_term_capital_gains",
    "E24515": "unrecaptured_section_1250_gain",
    "E24516": "capital_gain_less_investment_expense",
    "E24518": "28_percent_rate_gain_loss",
    "E24560": "non_schedule_d_tax",
    "E24598": "schedule_d_15_percent_tax_amount",
    "E24615": "schedule_d_25_percent_tax_amount",
    "E24570": "schedule_d_28_percent_tax_amount",
    "P25350": "rental_income",
    "P25380": "rent_royalty_interest_expenses",
    "E25550": "total_depreciation_depletion_all_property",
    "P25700": "rent_royalty_net_income_loss",
    "E25820": "deductible_rental_loss",
    "E25850": "rent_royalty_net_income",
    "E25860": "rent_royalty_net_loss",
    "E25940": "total_passive_income_partnerships",
    "E25980": "total_non_passive_income_partnerships",
    "E25920": "total_passive_loss_partnerships",
    "E25960": "total_non_passive_loss_partnerships",
    "E26110": "partnership_section_179_expense_deduction",
    "E26170": "total_passive_income_small_business_corp",
    "E26190": "total_non_passive_income_small_business_corp",
    "E26160": "total_passive_loss_small_business_corp",
    "E26180": "total_non_passive_loss_small_business_corp",
    "E26270": "partnership_s_corp_income",
    "E26100": "s_corp_section_179_expense_deduction",
    "E26390": "total_income_estate_trust",
    "E26400": "total_loss_estate_trust",
    "E27200": "farm_rent_income",
    "E30400": "self_employment_income_ss_tax_primary",
    "E30500": "self_employment_income_ss_tax_secondary",
    "E32800": "qualifying_individuals_expenses_form_2441",
    "E33000": "expenses_limited_to_earned_income_form_2441",
    "E53240": "work_opportunity_jobs_general_business_credit",
    "E53280": "research_experimentation_general_business_credit",
    "E53300": "low_income_housing_credit",
    "E53317": "employer_credit_social_security_tax_tips",
    "E58950": "total_investment_interest_expense_form_4952",
    "E58990": "investment_income_elected_amount_form_4952",
    "P60100": "net_operating_loss_tax_preference_adjustments_form_6251",
    "P61850": "total_adjustments_preferences_form_6251",
    "E60000": "taxable_income_amt_form_6251",
    "E62100": "alternative_minimum_taxable_income",
    "E62900": "alternative_tax_foreign_tax_credit",
    "E62720": "alternative_minimum_schedule_d_less_investment_interest",
    "E62730": "alternative_minimum_schedule_d_unrecaptured_section_1250_gain",
    "E62740": "alternative_minimum_capital_gain_amount",
    "P65300": "total_passive_net_income_form_8582",
    "P65400": "total_passive_losses_form_8582",
    "E68000": "total_losses_allowed_passive_activities",
    "E82200": "carry_forward_minimum_tax_credit_form_8801",
    "T27800": "farm_income",
    "S27860": "tentative_current_prior_year_tax_schedule_j",
    "P27895": "actual_prior_year_tax_schedule_j",
    "P87482": "american_opportunity_qualified_expenses_form_8863",
    "E87521": "american_opportunity_credit",
    "E87530": "lifetime_learning_total_qualified_expenses",
    "E87550": "lifetime_learning_credit",
    "P86421": "bond_purchase_amount_form_8888",
    "E85050": "total_rental_real_estate_royalties_partnerships_s_corps_trusts",
    "E85090": "total_net_gain_loss_disposition_property",
    "E85120": "total_investment_income",
    "E85180": "total_deductions_modifications",
    "E85570": "dependents_modified_adjusted_gross_income_amount_form_8962",
    "E85595": "annual_contribution_health_care_amount",
    "E85600": "monthly_contribution_health_care_amount",
    "E85770": "total_premium_tax_credit_amount",
    "E85775": "advance_premium_tax_credit_amount",
    "E85785": "excess_advance_payment_premium_tax_credit",
    "E85790": "repayment_limitation_amount",
    "RECID": "return_id",
    "S006": "decimal_weight",
    "S008": "sample_count",
    "S009": "population_count",
    "WSAMP": "sample_code",
    "TXRT": "marginal_tax_rate",
}

codebook.update(
    {
        "AGIR1": "adjusted_gross_income_band",
        "CLAIM8965": "health_coverage_exemptions",
        "DSI": "dependent_status_indicator",
        "EFI": "electronic_filing_indicator",
        "EIC": "earned_income_credit_code",
        "ELECT": "presidential_election_campaign_fund_boxes",
        "FDED": "form_of_deduction_code",
        "FLPDYR": "filing_accounting_period_year",
        "FLPDMO": "filing_accounting_period_month",
        "F2441": "form_2441_child_care_credit_qualified_individual",
        "F3800": "form_3800_general_business_credit",
        "F6251": "form_6251_alternative_minimum_tax",
        "F8582": "form_8582_passive_activity_loss_limitation",
        "F8606": "form_8606_nondeductible_ira_contributions",
        "F8829": "form_8829_expenses_home_business_use",
        "F8867": "form_8867_paid_preparer_earned_income_credit_checklist",
        "F8949": "form_8949_sales_dispositions_capital_assets",
        "F8959": "form_8959_additional_medicare_tax",
        "F8960": "form_8960_net_investment_income_tax",
        "F8962": "form_8962_premium_tax_credit",
        "F8965": "form_8965_health_coverage_exemptions",
        "IE": "itemized_deductions_election_indicator",
        "MARS": "marital_filing_status",
        "MIDR": "married_filing_separately_itemized_deductions_requirement_indicator",
        "N24": "number_children_child_tax_credit",
        "N25": "number_qualified_students_lifetime_learning_credit",
        "N30": "number_qualified_students_american_opportunity_credit",
        "PREP": "tax_preparer",
        "PREMNTHS": "months_enrolled_health_insurance_marketplace",
        "SCHB": "schedule_b_indicator",
        "SCHCF": "schedule_c_or_f_indicator",
        "SCHE": "schedule_e_indicator",
        "TFORM": "form_of_return",
        "TXST": "tax_status",
        "XFPT": "primary_taxpayer_exemption",
        "XFST": "secondary_taxpayer_exemption",
        "XOCAH": "exemptions_children_living_at_home",
        "XOCAWH": "exemptions_children_living_away_from_home",
        "XOODEP": "exemptions_other_dependents",
        "XOPAR": "exemptions_parents_living_at_away_from_home",
        "XTOT": "total_exemptions",
        "XTOT8962": "number_exemptions_form_8962",
        "XTOT8965": "number_exemptions_form_8965",
    }
)

codebook.update(
    {
        "AGEDP1": "age_dependent_1",
        "AGEDP2": "age_dependent_2",
        "AGEDP3": "age_dependent_3",
        "AGERANGE": "age_range_primary_filer",
        "EARNSPLIT": "earnings_split_joint_returns",
        "GENDER": "gender_primary_filer",
        "RECID": "return_id",
    }
)

CPS_DATASET = "cps_2023"


DEMOGRAPHIC_VARIABLES = [
    "age_dependent_1",
    "age_dependent_2",
    "age_dependent_3",
    "age_range_primary_filer",
    "earnings_split_joint_returns",
    "gender_primary_filer",
]

FINANCIAL_VARIABLES = [
    column
    for column in codebook.values()
    if column
    not in DEMOGRAPHIC_VARIABLES
    + [
        "return_id",
        "decimal_weight",
        "sample_count",
        "population_count",
        "sample_code",
    ]
]

FINANCIAL_SUBSET = [
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


def load_puf() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load the PUF and demographics data.

    Returns:
        puf (pd.DataFrame): The PUF data.
        puf_with_demographics (pd.DataFrame): The subset of the PUF data that has demographic information.
    """
    puf = pd.read_csv("~/Downloads/puf_2015.csv")
    demographics = pd.read_csv("~/Downloads/demographics_2015.csv")

    puf = puf.dropna()
    demographics = demographics.dropna()

    puf.S006 = puf.S006 / 100

    puf["taxable_interest_income"] = (
        puf.E00300 - puf.E00400
    )  # Taxable interest income = interest received - tax-exempt interest income
    puf["non_qualified_dividend_income"] = (
        puf.E00600 - puf.E00650
    )  # Non-qualified dividend income = dividends included in AGI - qualified dividend income

    puf = puf.rename(columns=codebook)
    demographics = demographics.rename(columns=codebook)
    return puf, demographics


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

    demographics_from_puf = Imputation()
    puf_with_demographics = puf[
        puf.return_id.isin(demographics.return_id)
    ].merge(demographics, on="return_id")

    soi = system.parameters.calibration.gov.irs.soi

    # Uprate the financial subset

    for variable_name in FINANCIAL_SUBSET:
        value_in_2015 = soi.children[variable_name]("2015-01-01")
        value_in_2023 = soi.children[variable_name]("2023-01-01")
        uprating_factor = value_in_2023 / value_in_2015
        puf_with_demographics[variable_name] = (
            puf_with_demographics[variable_name] * uprating_factor
        )

    demographics_from_puf.train(
        puf_with_demographics[FINANCIAL_VARIABLES],
        puf_with_demographics[DEMOGRAPHIC_VARIABLES],
    )

    puf_without_demographics = puf[
        ~puf.return_id.isin(puf_with_demographics.return_id)
    ].reset_index()
    puf_without_demographics.marital_filing_status = (
        puf_without_demographics.marital_filing_status.replace(
            {
                0: 1,
            }
        )
    )  # Aggregated returns -> single
    predicted_demographics = demographics_from_puf.predict(
        puf_without_demographics[FINANCIAL_VARIABLES]
    )
    puf_with_imputed_demographics = pd.concat(
        [puf_without_demographics, predicted_demographics], axis=1
    )

    weighted_puf_with_demographics = MicroDataFrame(
        puf_with_demographics, weights="decimal_weight"
    )
    weighted_puf_with_imputed_demographics = MicroDataFrame(
        puf_with_imputed_demographics, weights="decimal_weight"
    )

    puf_combined = pd.concat(
        [
            weighted_puf_with_demographics,
            weighted_puf_with_imputed_demographics,
        ]
    )
    puf_combined = MicroDataFrame(puf_combined, weights="decimal_weight")

    return puf_combined


def generate_puf_style_cps() -> pd.DataFrame:
    """Generate a PUF-style table from the CPS.

    Returns:
        cps (pd.DataFrame): The CPS data.
    """

    sim = Microsimulation(dataset=CPS_DATASET)

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

    filer_earned = sim.calculate("filer_earned")
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
    return cps_demographics


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
    income_from_demographics = Imputation()

    income_from_demographics.train(
        puf[DEMOGRAPHIC_VARIABLES],
        puf[FINANCIAL_SUBSET],
        sample_weight=puf.decimal_weight,
    )

    cps_financial_predictions = income_from_demographics.predict(
        cps_demographics[DEMOGRAPHIC_VARIABLES],
        mean_quantile=[0.9] + [0.5] * (len(FINANCIAL_SUBSET) - 1),
    )
    cps_imputed = pd.concat(
        [cps_demographics, cps_financial_predictions], axis=1
    )
    cps_imputed = MicroDataFrame(
        cps_imputed, weights=cps_demographics.tax_unit_weight
    )

    return cps_imputed


def project_tax_unit_cps_to_person_level(
    puf_style_cps: pd.DataFrame,
) -> pd.DataFrame:
    """Project tax unit CPS to person level.

    Args:
        puf_style_cps (pd.DataFrame): The CPS data with imputed financial information.

    Returns:
        person_df (pd.DataFrame): The CPS data with imputed financial information projected to the person level.
    """
    sim = Microsimulation(dataset=CPS_DATASET)
    person_df = pd.DataFrame(
        dict(
            person_id=sim.calculate("person_id").values,
            tax_unit_id=sim.calculate("person_tax_unit_id").values,
        )
    )

    person_is_tax_filer_head = sim.calculate("is_tax_unit_head").values

    for variable in FINANCIAL_SUBSET:
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
            cps_share_of_tax_unit_original_total * mapped_down_imputed_values
        )

    person_df = person_df.fillna(0)
    return person_df


def puf_imputed_cps_person_level(
    verbose: bool = False,
) -> pd.DataFrame:
    """Generate a PUF-imputed CPS at the person level.

    Args:
        verbose (bool): Whether to print progress statements.

    Returns:
        person_level_puf_imputed_cps (pd.DataFrame): The PUF-imputed CPS at the person level.
    """
    if verbose:
        print("Loading PUF and demographics")
    puf, demographics = load_puf()

    if verbose:
        print("Imputing missing demographics")
    puf = impute_missing_demographics(puf, demographics)

    if verbose:
        print("Generating PUF-style CPS")
    puf_style_cps = generate_puf_style_cps()

    if verbose:
        print("Imputing PUF financials to CPS")
    puf_imputed_cps = impute_puf_financials_to_cps(puf_style_cps, puf)

    if verbose:
        print("Projecting tax unit CPS to person level")
    person_level_puf_imputed_cps = project_tax_unit_cps_to_person_level(
        puf_imputed_cps
    )

    if verbose:
        print("Done")
    return person_level_puf_imputed_cps


if __name__ == "__main__":
    puf_imputed_cps_person_level(verbose=True)
