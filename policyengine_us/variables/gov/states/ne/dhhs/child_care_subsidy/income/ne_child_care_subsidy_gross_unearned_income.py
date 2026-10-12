from policyengine_us.model_api import *


class ne_child_care_subsidy_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = YEAR
    label = "Nebraska Child Care Subsidy gross unearned income"
    defined_for = StateCode.NE
    adds = "gov.states.ne.dhhs.child_care_subsidy.income.sources.unearned"
    reference = (
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=3",
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=4",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=12",
    )
