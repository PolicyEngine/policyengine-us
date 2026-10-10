from policyengine_us.model_api import *


class medicaid_ltss_spouses_months_in_same_institutional_facility(Variable):
    value_type = int
    entity = MaritalUnit
    label = (
        "Completed months both spouses have resided in the same institutional facility"
    )
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Number of completed months both spouses have resided together in "
        "the same institutional facility. Delaware DSSM 20810 permits the "
        "couple to elect individual budgeting after six months. Defaults "
        "to zero, treating an unspecified duration as before the election "
        "is available. This input does not select the budgeting regime."
    )
    reference = "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67"
