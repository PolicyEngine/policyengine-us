from policyengine_us.model_api import *


class ms_wd_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Mississippi Working Disabled gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.medicaid.ms.gov/wp-content/uploads/2014/01/Admin-Code-Part-104.pdf#page=8"
    defined_for = StateCode.MS

    adds = "gov.states.ms.dom.wd.eligibility.income.sources.unearned"
