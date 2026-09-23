from policyengine_us.model_api import *


class ar_agi_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas adjusted gross income for each individual"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=22"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        gross_income = person("ar_gross_income_joint", period)
        income_exemptions = person("ar_exemptions", period)
        net_income = gross_income - income_exemptions
        # On a return that is not married filing separately on the same
        # return, all income goes in Column A, so one spouse's loss offsets
        # the other's income; the tax unit total is floored at zero when it
        # is used as a tax base.
        # Allocate any dependent net income (floored at zero) to the head.
        is_dependent = person("is_tax_unit_dependent", period)
        sum_dep_net_income = person.tax_unit.sum(is_dependent * max_(net_income, 0))
        is_head = person("is_tax_unit_head", period)
        return ~is_dependent * net_income + is_head * sum_dep_net_income
