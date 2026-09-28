from policyengine_us.model_api import *


class mo_sab_reported_earnings_taxes(Variable):
    value_type = float
    entity = Person
    label = "Missouri SAB taxes on earnings"
    documentation = (
        "Monthly federal and state income tax and Social Security tax withheld "
        "from or paid on this person's earnings, plus mandatory city earnings "
        "tax paid. Do not include taxes on unearned income. Defaults to zero; "
        "no tax deduction is estimated when no amount is entered. For gross "
        "monthly earnings up to $1,200, 13 CSR 40-2.120(8) budgets a standard "
        "tax amount from a table instead, which is not modeled. A monthly entry "
        "carries forward to later months and years, uprated in later years, "
        "until changed; enter zero when payments stop."
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-05/0410-015-05-20/",
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-05/0410-015-05-25/",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120",
    )
