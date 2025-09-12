from policyengine_us.model_api import *


class ma_ccfa_family_child_care_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) family child care reimbursement amount per child"
    unit = USD
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.eec.ccfa.reimbursement_rates.family_child_care
        region = person.household("ma_ccfa_region", period)
        age = person("monthly_age", period)
        return where(
            age >= p.age_threshold, p.older[region], p.younger[region]
        )
