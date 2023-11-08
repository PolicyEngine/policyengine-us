from policyengine_us.model_api import *


class nj_agi_subtractions(Variable):
    value_type = float
    entity = Person
    label = "New Jersey subtractions from federal AGI by person"
    unit = USD
    documentation = "Subtractions from federal AGI to get NJ total income."
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/"

    adds = "gov.states.nj.tax.income.subtractions"
