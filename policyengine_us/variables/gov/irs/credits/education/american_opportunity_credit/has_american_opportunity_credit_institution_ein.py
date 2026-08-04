from policyengine_us.model_api import *


class has_american_opportunity_credit_institution_ein(Variable):
    value_type = bool
    entity = Person
    label = "Has institution EIN for American Opportunity Credit"
    documentation = "Whether the filer includes the employer identification number of the eligible educational institution for this student's American Opportunity Credit expenses."
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"
