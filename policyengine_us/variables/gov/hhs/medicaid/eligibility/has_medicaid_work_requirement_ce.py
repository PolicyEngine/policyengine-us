from policyengine_us.model_api import *


class has_medicaid_work_requirement_ce(Variable):
    value_type = bool
    entity = Person
    label = "Has demonstrated Community Engagement (CE) compliance for Medicaid work requirements"
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters) -> bool:
        enrolled_half_time = person("enrolled_half_time_or_more", period)
        
        monthly_hours_worked = person("ce_activity_hours", period)
        hours_threshold = parameters(period).gov.hhs.medicaid.eligibility.work_requirements.monthly_hours_threshold
        passed_hours: bool = monthly_hours_worked >= hours_threshold
        
        monthly_income_earned = person("ce_activity_income", period)
        income_threshold = person("medicaid_work_income_threshold", period)
        passed_income: bool = monthly_income_earned >= income_threshold

        return enrolled_half_time or passed_hours or passed_income
