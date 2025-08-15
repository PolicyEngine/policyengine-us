from policyengine_us.model_api import *


class ma_ccfa_maximum_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) maximum reimbursement amount per child"
    unit = USD
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
    definition_period = MONTH
    defined_for = StateCode.MA

    adds = [
        "ma_ccfa_center_based_early_education_reimbursement",
        "ma_ccfa_center_based_school_age_reimbursement",
        "ma_ccfa_head_start_partner_and_kindergarten_reimbursement",
        "ma_ccfa_informal_child_care_reimbursement",
        "ma_ccfa_family_child_care_reimbursement",
    ]
