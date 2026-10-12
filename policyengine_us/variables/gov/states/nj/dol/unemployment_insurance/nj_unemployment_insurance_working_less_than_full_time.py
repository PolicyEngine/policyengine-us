from policyengine_us.model_api import *


class nj_unemployment_insurance_working_less_than_full_time(Variable):
    value_type = bool
    entity = Person
    label = "New Jersey unemployment insurance claimant is working less than full-time"
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.nj.gov/labor/myunemployment/help/faqs/reducebenefits.shtml",
        "https://www.nj.gov/labor/ea/help/employer_handbook/ui.shtml",
    )
    defined_for = StateCode.NJ
