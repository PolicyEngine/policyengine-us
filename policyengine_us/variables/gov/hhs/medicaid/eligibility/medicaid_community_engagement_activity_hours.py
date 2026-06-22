from policyengine_us.model_api import *


class medicaid_community_engagement_activity_hours(Variable):
    value_type = float
    entity = Person
    label = "Medicaid community engagement qualifying monthly activity hours"
    unit = "hour"
    definition_period = YEAR
    documentation = (
        "Monthly hours that can satisfy Medicaid community engagement through "
        "work, community service, work programs, or less-than-half-time "
        "education combined with other qualifying activities."
    )
    adds = [
        "monthly_hours_worked",
        "medicaid_community_engagement_community_service_hours",
        "medicaid_community_engagement_work_program_hours",
        "medicaid_community_engagement_less_than_half_time_education_hours",
    ]

