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
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Part_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Benton-Washington_Co_Part_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/2025-2027_CCDF_State_Plan_Final_4.26.24.1REV_OEC.pdf#page=39",
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=20",
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
        # CCDF State Plan §3.1.1 caps family copay at 4% of monthly income.
        # FSU §4.3.3 (file p.20) excludes children's SSI and Social Security
        # from the budget, so the cap base is countable (adult) income — not
        # the literal "gross income" wording.
        p = parameters(period).gov.states.ar.ade.oec.sra.rates
        # Each child's payable copay is the lesser of the rate-sheet copay and
        # the child's actual provider charge — a child whose expense is below
        # the scheduled copay does not owe the full scheduled amount.
        payable_copay = min_(monthly_copay, monthly_expense)
        total_payable_copay = spm_unit.sum(payable_copay * is_eligible_child)
        # Clamp at 0 so a self-employment loss doesn't inflate cap_savings.
        countable_income = max_(spm_unit("ar_sra_countable_income", period), 0)
        copay_ceiling = p.max_copay_share_of_gross_income * countable_income
        cap_savings = max_(total_payable_copay - copay_ceiling, 0)
        total_expense = spm_unit.sum(monthly_expense * is_eligible_child)
        return min_(total_uncapped_subsidy + cap_savings, total_expense)
