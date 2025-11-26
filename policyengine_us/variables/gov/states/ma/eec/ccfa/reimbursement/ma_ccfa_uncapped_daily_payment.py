from policyengine_us.model_api import *


class ma_ccfa_uncapped_daily_payment(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) uncapped daily payment per child"
    unit = USD
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        center_based_early_education_payment = person(
            "ma_ccfa_center_based_early_education_reimbursement", period
        )
        center_based_school_age_payment = person(
            "ma_ccfa_center_based_school_age_reimbursement", period
        )
        head_start_partner_and_kindergarten_payment = person(
            "ma_ccfa_head_start_partner_and_kindergarten_reimbursement", period
        )
        informal_child_care_payment = person(
            "ma_ccfa_informal_child_care_reimbursement", period
        )
        family_child_care_payment = person(
            "ma_ccfa_family_child_care_reimbursement", period
        )

        care_provider_type = person("ma_ccfa_care_provider_type", period)
        care_provider_types = care_provider_type.possible_values
        center_based_early_education = (
            care_provider_type
            == care_provider_types.CENTER_BASED_CARE_EARLY_EDUCATION
        )
        center_based_school_age = (
            care_provider_type
            == care_provider_types.CENTER_BASED_CARE_SCHOOL_AGE
        )
        head_start_partner_and_kindergarten = (
            care_provider_type
            == care_provider_types.HEAD_START_PARTNER_AND_KINDERGARTEN
        )
        informal_child_care = (
            care_provider_type == care_provider_types.INFORMAL_CHILD_CARE
        )
        family_child_care = (
            care_provider_type == care_provider_types.FAMILY_CHILD_CARE
        )
        return select(
            [
                center_based_early_education,
                center_based_school_age,
                head_start_partner_and_kindergarten,
                informal_child_care,
                family_child_care,
            ],
            [
                center_based_early_education_payment,
                center_based_school_age_payment,
                head_start_partner_and_kindergarten_payment,
                informal_child_care_payment,
                family_child_care_payment,
            ],
            default=0,
        )
