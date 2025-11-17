from policyengine_us.model_api import *


class il_hbwd_gross_unearned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities gross unearned income"
    definition_period = MONTH
    reference = (
        "https://ilga.gov/commission/jcar/admincode/089/089001200I03300R.html",
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
    )
    defined_for = StateCode.IL

    adds = "gov.states.il.hfs.hbwd.income.sources.unearned"
