from policyengine_us.model_api import *


class fl_tca_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TCA payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://www.law.cornell.edu/regulations/florida/Fla-Admin-Code-Ann-R-65A-4-220",
    )
    defined_for = StateCode.FL

    def formula(spm_unit, period, parameters):
        # Per Florida Statutes 414.095(10): Payment based on shelter tier
        # Per FAC 65A-4.220(2)(b): Shelter obligation = responsibility to pay for cost of housing
        # Uses pre-subsidy rent to avoid circular dependency:
        # tanf -> fl_tca -> housing_cost -> rent -> housing_assistance -> hud_annual_income -> tanf
        p = parameters(period).gov.states.fl.dcf.tanf

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
        monthly_shelter = pre_subsidy_rent + other_housing

        # Determine unit size, capped at max in parameter table
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_family_size)

        # Determine payment standard based on shelter tier
        threshold = p.shelter_cost_threshold
        zero_shelter = monthly_shelter == 0
        low_shelter = (monthly_shelter > 0) & (monthly_shelter <= threshold)

        return select(
            [zero_shelter, low_shelter],
            [
                p.payment_standard.zero_shelter[capped_size],
                p.payment_standard.low_shelter[capped_size],
            ],
            default=p.payment_standard.high_shelter[capped_size],
        )
