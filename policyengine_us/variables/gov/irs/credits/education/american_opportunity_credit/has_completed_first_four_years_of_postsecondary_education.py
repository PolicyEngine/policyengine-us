from policyengine_us.model_api import *


class has_completed_first_four_years_of_postsecondary_education(Variable):
    value_type = bool
    entity = Person
    label = "Completed the first four years of postsecondary education"
    documentation = "Whether the student completed the first four years of postsecondary education before the beginning of the tax year."
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"
