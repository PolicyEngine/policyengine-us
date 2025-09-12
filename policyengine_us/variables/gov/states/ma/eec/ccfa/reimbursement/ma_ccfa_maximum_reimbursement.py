from policyengine_us.model_api import *


class ma_ccfa_maximum_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) maximum reimbursement amount per child"
    unit = USD
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        daily_payment = person("ma_ccfa_uncapped_daily_payment", period)
        reimbursement_multiplier = person(
            "ma_ccfa_reimbursement_ratio", period
        )
        attending_days_per_month = person(
            "childcare_attending_days_per_month", period.this_year
        )
        return (
            daily_payment * reimbursement_multiplier * attending_days_per_month
        )
