from policyengine_us.model_api import *


class sd_cca_parent_in_eligible_activity(Variable):
    value_type = bool
    entity = Person
    label = "South Dakota CCA parent in an eligible activity"
    definition_period = MONTH
    defined_for = StateCode.SD
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/BEES_CCA_Policy_Manual.pdf#page=35",
        "https://dss.sd.gov/docs/childcare/assistance/BEES_CCA_Policy_Manual.pdf#page=37",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.work_requirement
        min_wage = parameters(period).gov.dol.minimum_wage
        weekly_hours = person("weekly_hours_worked", period.this_year)
        # BEES Section 10.1.1 converts weekly hours with a 4.3 factor and
        # rounds the result up to the next whole monthly hour.
        monthly_hours = np.ceil(weekly_hours * p.weekly_to_monthly_factor)
        # An employed caretaker must work at least 80 hours per month at a
        # salary equivalent to the federal minimum wage (BEES Manual Section
        # 7.1).
        employment_income = person("employment_income", period)
        meets_employment_requirement = (monthly_hours >= p.monthly_hours) & (
            employment_income >= monthly_hours * min_wage
        )
        # A self-employed caretaker must establish at least 80 hours per month
        # through both reported work hours and net earnings at the federal
        # minimum wage; a business loss counts as zero earnings (BEES Manual
        # Sections 7.1 and 8.3.1). BEES Section 10.1.1 instead derives
        # self-employment hours from net income (monthly income divided by the
        # federal minimum wage, converted with the 4.3 factor); as a
        # simplification, reported work hours stand in for that derivation, so
        # a caretaker whose reported hours fall short of the income-derived
        # hours does not qualify through this path.
        self_employment_income = person("self_employment_income", period)
        meets_self_employment_requirement = (monthly_hours >= p.monthly_hours) & (
            self_employment_income >= p.monthly_hours * min_wage
        )
        # Full-time students meet the 12-semester-credit-hour minimum; the
        # combined 80-hour work-plus-school path and positive TANF activity
        # hours are represented through the CCDF activity-test fallback.
        # TANF enrollment alone does not qualify a caretaker because deferred
        # recipients can have no TANF activity hours.
        is_student = person("is_full_time_student", period.this_year)
        return (
            meets_employment_requirement
            | meets_self_employment_requirement
            | is_student
        )
