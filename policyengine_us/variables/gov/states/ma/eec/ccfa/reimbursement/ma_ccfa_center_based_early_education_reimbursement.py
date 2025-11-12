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
        return p.early_education[region][age_category]
