from policyengine_us.model_api import *


class ri_pregnancy_end_date(Variable):
    value_type = date
    entity = Person
    label = "End date of the last completed pregnancy for Rhode Island Medicaid"
    documentation = (
        "End date of the last completed pregnancy, whether by birth, "
        "miscarriage or termination. It describes the same event as "
        "count_days_postpartum; if the two disagree, the day-count postpartum "
        "route and Rhode Island's calendar continuation are both applied, and "
        "either one qualifies. The input is annual: a value entered only for "
        "the year the pregnancy ended gives no continuation in later years."
    )
    definition_period = YEAR
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm"
    )
