from policyengine_us.model_api import *


class il_hbwd_person(Variable):
    value_type = float
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://hfs.illinois.gov/medicalprograms/hbwd.html",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
    )
    defined_for = "il_hbwd_eligible"

    def formula(person, period, parameters):
        # HBWD provides comprehensive healthcare coverage
        # Could model as:
        # 1. Negative premium (cost to individual)
        # 2. Imputed healthcare value minus premium
        # 3. Healthcare coverage indicator
        # For now, return negative premium as cost
        premium = person("il_hbwd_premium", period)
        return -premium
