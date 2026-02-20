from policyengine_us.model_api import *


class az_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.azleg.gov/ars/46/00207-01.htm",
        "https://www.azleg.gov/ars/46/00207.htm",
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Arizona uses monthly 1992 FPG baseline for payment standard
        # az_tanf_fpg_baseline is YEAR, auto-converted to monthly when called from MONTH context
        monthly_fpg_baseline = spm_unit("az_tanf_fpg_baseline", period)

        p = parameters(period).gov.states.az.hhs.tanf.payment_standard

        # Base payment standard (A1) per A.R.S. § 46-207.01
        base_standard = p.rate * monthly_fpg_baseline

        # A2 = A1 reduced by 37% for those without shelter costs per A.R.S. § 46-207
        # Uses pre-subsidy rent to avoid circular dependency:
        # tanf -> az_tanf -> housing_cost -> rent -> housing_assistance
        # -> hud_annual_income -> tanf
        pre_subsidy_rent = add(spm_unit, period, ["pre_subsidy_rent"])
        other_housing = add(
            spm_unit,
            period,
            [
                "real_estate_taxes",
                "homeowners_association_fees",
                "mortgage_payments",
                "homeowners_insurance",
            ],
        )
        has_shelter_costs = (pre_subsidy_rent + other_housing) > 0

        reduced_standard = base_standard * (1 - p.reduction)

        return where(has_shelter_costs, base_standard, reduced_standard)
