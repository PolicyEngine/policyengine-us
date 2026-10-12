from policyengine_us.model_api import *


class attends_eligible_educational_institution_for_american_opportunity_credit(
    Variable
):
    value_type = bool
    entity = Person
    label = "Attends an AOTC eligible educational institution"
    documentation = "Whether the student attends a post-secondary educational institution eligible to participate in a US Department of Education student aid program for American Opportunity Credit purposes."
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"
