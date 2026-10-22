from policyengine_us.model_api import *


class ri_medicaid_pregnancy_end_date(Variable):
    value_type = date
    entity = Person
    label = "End date of the last completed pregnancy for Rhode Island Medicaid"
    definition_period = YEAR
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm"
    )
