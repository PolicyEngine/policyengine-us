from policyengine_us.model_api import *


class il_hbwd_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities income eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbwd.eligibility
        # Income limit is 350% of FPL
        fpg = person.spm_unit("spm_unit_fpg", period)
        income_limit = fpg * p.income.limit
        # Check household countable income against limit
        # Per § 120.510(f), counts individual + spouse income
        countable_income = person.spm_unit("il_hbwd_countable_income", period)
        return countable_income <= income_limit
