from policyengine_us.model_api import *


class ma_ccfa_center_based_early_education_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) center-based early education reimbursement amount per child"
    unit = USD
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.eec.ccfa.reimbursement_rates.center_based
        region = person.household("ma_ccfa_region", period)
        age_category = person("ma_ccfa_child_age_category", period)
        uncapped_payment_per_day = p.early_education[region][age_category]
        reimbursement_multiplier = person(
            "ma_ccfa_reimbursement_ratio", period
        )
        attending_days_per_month = person(
            "childcare_attending_days_per_month", period
        )
        care_provider_type = person("ma_ccfa_care_provider_type", period)
        center_based_early_education = (
            care_provider_type
            == care_provider_type.possible_values.CENTER_BASED_CARE_EARLY_EDUCATION
        )
        return (
            uncapped_payment_per_day
            * attending_days_per_month
            * reimbursement_multiplier
            * center_based_early_education
        )
