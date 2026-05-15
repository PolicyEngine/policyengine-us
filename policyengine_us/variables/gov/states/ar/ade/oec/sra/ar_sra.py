from policyengine_us.model_api import *


class ar_sra(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Arkansas School Readiness Assistance benefit amount"
    definition_period = MONTH
    defined_for = "is_ar_sra_eligible"
    reference = (
        "https://dese.ade.arkansas.gov/Files/SRA_Sliding_Fee_Scale_with_Rates_&_Copays--Statewide_Full_Time_20251101_OEC.pdf",
        "https://dese.ade.arkansas.gov/Files/R_&_R__Nov_2025_(English)_(1)_OEC.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_eligible_child = person("is_ar_sra_child_eligible", period)
        daily_state_payment = person("ar_sra_daily_state_payment", period)
        daily_copay = person("ar_sra_daily_copay", period)
        attending_days = person("childcare_attending_days_per_month", period.this_year)
        monthly_max_state_payment = daily_state_payment * attending_days
        monthly_copay = daily_copay * attending_days
        annual_expense = person("pre_subsidy_childcare_expenses", period.this_year)
        monthly_expense = annual_expense / MONTHS_IN_YEAR
        subsidy = min_(
            max_(monthly_expense - monthly_copay, 0),
            monthly_max_state_payment,
        )
        return spm_unit.sum(subsidy * is_eligible_child)
