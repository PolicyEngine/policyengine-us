from policyengine_us.model_api import *


class has_felony_drug_conviction(Variable):
    value_type = bool
    entity = Person
    label = "Has a felony drug conviction"
    documentation = "Whether the person has been convicted of a Federal or State felony offense consisting of the possession or distribution of a controlled substance before the end of the tax year."
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"
