from policyengine_us.model_api import *


class ma_ccfa_center_based_reimbursement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) center-based care reimbursement amount per child"
    unit = USD
    reference = "https://www.mass.gov/doc/eecfy26-rate-increase-chart/download#page=1"
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.reimbursement_rates.center_based
        region = person.household("ma_ccfa_region", period)
        age_category = person("ma_ccfa_child_age_category", period)
        schedule_type = person("ma_ccfa_schedule_type", period)
        # NOTE: The rate chart prices center-based care in one table whose early
        # education columns are keyed by age alone and whose school age columns
        # are keyed by schedule, so the child's age category picks the columns.
        is_school_age = age_category == age_category.possible_values.SCHOOL_AGE
        return where(
            is_school_age,
            p.school_age[region][age_category][schedule_type],
            p.early_education[region][age_category],
        )
