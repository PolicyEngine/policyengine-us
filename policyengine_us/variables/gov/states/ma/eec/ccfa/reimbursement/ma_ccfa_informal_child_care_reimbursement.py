from policyengine_us.model_api import *


class ma_ccfa_informal_child_care_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) informal child care reimbursement amount per child"
    unit = USD
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.eec.ccfa.reimbursement_rates.informal_child_care
        is_relative_home_care = person("ma_ccfa_is_relative_home_care", period)
        uncapped_payment_per_day = where(
            is_relative_home_care, p.relative_home, p.child_home
        )
        reimbursement_multiplier = person(
            "ma_ccfa_reimbursement_ratio", period
        )
        attending_days_per_month = person(
            "ma_ccfa_attending_days_per_month", period
        )
        care_provider_type = person("ma_ccfa_care_provider_type", period)
        informal_child_care = (
            care_provider_type
            == care_provider_type.possible_values.INFORMAL_CHILD_CARE
        )
        return (
            uncapped_payment_per_day
            * attending_days_per_month
            * reimbursement_multiplier
            * informal_child_care
        )
