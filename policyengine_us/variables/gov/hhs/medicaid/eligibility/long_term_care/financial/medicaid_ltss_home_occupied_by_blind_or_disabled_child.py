from policyengine_us.model_api import *


class medicaid_ltss_home_occupied_by_blind_or_disabled_child(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid LTSS home occupied by blind or disabled child"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Explicit indication that the applicant's blind or disabled child "
        "lawfully resides in the home for the Medicaid LTSS home-equity "
        "exception. The model does not adjudicate disability, relationship, "
        "or residence."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396p#f_2"
