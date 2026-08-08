from policyengine_us.model_api import *


class ne_child_care_subsidy_approved_absence_days(Variable):
    value_type = int
    entity = Person
    unit = "day"
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy approved billable absence days"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=23",
        "https://dhhs.ne.gov/Child%20Care%20Documents/Rate%20Structure%20Frequently%20Asked%20Questions%20%28FAQ%29.pdf#page=1",
    )
