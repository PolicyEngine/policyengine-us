from policyengine_us.model_api import *


class worked_last_year(Variable):
    value_type = bool
    entity = Person
    label = "worked at any time in the previous year"
    documentation = (
        "Whether the person worked at any time during the previous year: "
        "the WKSWORK variable in the Current Population Survey exceeding "
        "zero, which is the universe condition of the work-experience "
        "longest-job recodes (detailed_occupation_recode, "
        "detailed_industry_recode, major_industry_recode)."
    )
    definition_period = YEAR
