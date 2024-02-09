from policyengine_us.model_api import *


class la_adoption_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana adoption credit"
    reference = "https://legis.la.gov/legis/Law.aspx?d=1336834"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    adds = ["la_adoption_credit_person"]
