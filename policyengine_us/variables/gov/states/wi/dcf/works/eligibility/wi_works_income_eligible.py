from policyengine_us.model_api import *


class wi_works_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin Works income eligible"
    definition_period = MONTH
    reference = (
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/03.2.1_115_Percent_Gross_Income_Test.htm",
        "https://docs.legis.wisconsin.gov/code/register/2021/790b/insert/dcf101.pdf#page=5",
    )
    defined_for = StateCode.WI

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("wi_works_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        p = parameters(period).gov.states.wi.dcf.works.income_limit
        income_limit = fpg * p.rate
        return countable_income <= income_limit
