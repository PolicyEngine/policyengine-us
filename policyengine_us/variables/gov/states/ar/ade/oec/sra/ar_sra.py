from policyengine_us.model_api import *


class ar_sra(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas School Readiness Assistance benefit amount"
    unit = USD
    definition_period = MONTH
    defined_for = "is_ar_sra_eligible"
    reference = (
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/2025-2027_CCDF_State_Plan_Final_4.26.24.1REV_OEC.pdf#page=39",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_eligible_child = person("is_ar_sra_child_eligible", period)
        daily_state_payment = person("ar_sra_daily_state_payment", period)
        daily_copay = person("ar_sra_daily_copay", period)
        attending_days = person("childcare_attending_days_per_month", period.this_year)
        monthly_max_state_payment = daily_state_payment * attending_days
        monthly_copay = daily_copay * attending_days
        monthly_expense = person("pre_subsidy_childcare_expenses", period)
        uncapped_subsidy = min_(
            max_(monthly_expense - monthly_copay, 0),
            monthly_max_state_payment,
        )
        total_uncapped_subsidy = spm_unit.sum(uncapped_subsidy * is_eligible_child)
        # CCDF State Plan §3.1.1 caps the family copay at 4% of gross income
        # per family, regardless of the number of children. When rate-sheet
        # copays sum above the cap, the state covers the gap.
        p = parameters(period).gov.states.ar.ade.oec.sra.rates
        total_uncapped_copay = spm_unit.sum(monthly_copay * is_eligible_child)
        # Clamp at 0 so a negative countable income (e.g. self-employment
        # loss) doesn't inflate cap_savings.
        countable_income = max_(spm_unit("ar_sra_countable_income", period), 0)
        copay_ceiling = p.max_copay_share_of_gross_income * countable_income
        cap_savings = max_(total_uncapped_copay - copay_ceiling, 0)
        # State subsidy never exceeds the family's actual childcare cost.
        total_expense = spm_unit.sum(monthly_expense * is_eligible_child)
        return min_(total_uncapped_subsidy + cap_savings, total_expense)
