from policyengine_us.model_api import *


class mo_sab_tax_exemption(Variable):
    value_type = float
    entity = Person
    label = "Missouri SAB taxes on earnings"
    # Report federal and state income tax and Social Security tax withheld from or
    # paid on this person's earnings, plus mandatory city earnings tax paid. Do
    # not include taxes on unearned income. Enter zero when payments stop;
    # monthly inputs otherwise carry forward to later periods.
    unit = USD
    definition_period = MONTH
    default_value = 0
    defined_for = StateCode.MO
    reference = (
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-05/0410-015-05-20/",
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-05/0410-015-05-25/",
    )
