from policyengine_us.model_api import *


class il_hbwd_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities income eligible"
    definition_period = MONTH
    reference = (
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbwd.eligibility
        # Income limit is 350% of FPL
        fpg = person.spm_unit("spm_unit_fpg", period)
        income_limit = fpg * p.income_limit_fpg_percent
        # Check countable income against limit
        countable_income = person("il_hbwd_countable_income", period)
        return countable_income <= income_limit
