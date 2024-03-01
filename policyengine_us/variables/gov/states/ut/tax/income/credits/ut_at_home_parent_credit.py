from policyengine_us.model_api import *


class ut_at_home_parent_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah at-home parent credit"
    unit = USD
    definition_period = YEAR
    defined_for = "ut_at_home_parent_credit_eligible"
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1005.html",
        "https://www.taxformfinder.org/forms/2021/2021-utah-tc-40-full-packet.pdf#page=23",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        p = parameters(period).gov.states.ut.tax.income.credits.at_home_parent
        count_children = tax_unit.sum((age < p.max_child_age) & is_dependent)

        is_joint = tax_unit("tax_unit_is_joint", period)
        at_home_parent_credit = p.amount * count_children
        return where(
            is_joint, at_home_parent_credit * 2, at_home_parent_credit
        )
