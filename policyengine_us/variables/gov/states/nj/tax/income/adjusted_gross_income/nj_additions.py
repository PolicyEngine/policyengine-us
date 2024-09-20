from policyengine_us.model_api import *


class nj_additions(Variable):
    value_type = float
    entity = Person
    label = "New Jersey additions to federal AGI by person"
    unit = USD
    documentation = "Additions to federal AGI to get NJ total income."
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/"
    defined_for = StateCode.NJ
