from policyengine_us.model_api import *


class la_receives_blind_exemption(Variable):
    value_type = bool
    entity = Person
    label = "Filer receives the Louisiana blind exemption over the subtraction"
    definition_period = YEAR
    #  RS 47:44.1 indicates that filers can only take either the exemption or subtraction.
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=102133"
    defined_for = StateCode.LA
    default_value = True
