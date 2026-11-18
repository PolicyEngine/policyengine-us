from policyengine_us.model_api import *


class medicaid_ltss_home_occupied_by_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid LTSS home occupied by spouse"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Explicit indication that the applicant's spouse lawfully resides in "
        "the home for the Medicaid LTSS home-equity exception. The model does "
        "not infer residence from household membership."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396p#f_2"
