from policyengine_us.model_api import *


class weeks_unemployed(Variable):
    value_type = float
    entity = Person
    label = "weeks spent looking for work"
    unit = "week"
    reference = "https://www2.census.gov/programs-surveys/cps/techdocs/cpsmar24.pdf"
    definition_period = YEAR
