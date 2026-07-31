from policyengine_us.model_api import *


class ne_child_care_subsidy_registration_fee_count(Variable):
    value_type = int
    entity = Person
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy approved registration fee count"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=22",
    )
