from policyengine_us.model_api import *


class nj_unemployment_insurance_weeks_claimed(Variable):
    value_type = int
    entity = Person
    label = "New Jersey unemployment insurance weeks claimed"
    unit = "week"
    definition_period = YEAR
    reference = "https://www.nj.gov/labor/myunemployment/assets/pdfs/UI_statute.pdf"
    defined_for = StateCode.NJ
