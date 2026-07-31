from policyengine_us.model_api import *


class ne_child_care_subsidy_new_provider(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy new or changed provider"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=22",
    )
