from policyengine_us.model_api import *


class ny_ui_weekly_hours_worked(Variable):
    value_type = float
    entity = Person
    label = "New York unemployment insurance weekly claim hours worked"
    unit = "hour"
    definition_period = YEAR
    default_value = 0
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
    documentation = (
        "Claim-week UI hours, after applying NYSDOL P803 reporting rules to "
        "round up to whole hours and cap each work day at 10 hours; these "
        "conventions are upstream of this input and assumed already applied. "
        "This is distinct from average weekly work hours. The annual definition "
        "period treats the value as a single representative claim week."
    )
    defined_for = StateCode.NY
