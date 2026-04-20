from policyengine_us.model_api import *


class nj_unemployment_insurance_weekly_gross_wages(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance weekly gross wages while claiming benefits"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.nj.gov/labor/myunemployment/help/faqs/reducebenefits.shtml",
    )
    defined_for = StateCode.NJ
