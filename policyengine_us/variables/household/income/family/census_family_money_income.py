from policyengine_us.model_api import *


class census_family_money_income(Variable):
    value_type = float
    entity = Family
    label = "Census family money income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Census Bureau money income of the family: census_money_income summed "
        "over every member. Census families are two or more people related by "
        "birth, marriage or adoption who live together, and it tabulates "
        "people living without relatives as unrelated individuals; a model "
        "family can have one member."
    )
    reference = (
        "https://www2.census.gov/programs-surveys/cps/methodology/Appendix%20A%20P60-200%20income%20measurement%20definition.pdf#page=1",
        "https://cps.ipums.org/cps-action/variables/FTOTVAL",
    )
    adds = ["census_money_income"]
