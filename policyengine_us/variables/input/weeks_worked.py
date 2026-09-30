from policyengine_us.model_api import *


class weeks_worked(Variable):
    value_type = int
    entity = Person
    label = "Weeks worked during the year"
    unit = "week"
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Weeks worked during the year (ACS WKWN, 1-52; CPS ASEC WKSWORK, "
        "0-52). Zero means the person did not work or the value was not "
        "reported. Pure input: a value supplied for an earlier year is "
        "carried forward to later years by auto_carry_over_input_variables."
    )
    reference = (
        "https://api.census.gov/data/2023/acs/acs1/pums/variables/WKWN.json",
        "https://www2.census.gov/programs-surveys/cps/techdocs/cpsmar24.pdf",
    )
