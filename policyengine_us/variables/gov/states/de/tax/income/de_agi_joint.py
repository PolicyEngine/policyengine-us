from policyengine_us.model_api import *


class de_agi_joint(Variable):
    value_type = float
    entity = Person
    label = (
        "Delaware adjusted gross income for each individual whe married filing jointly"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        pre_exclusions_agi = person("de_pre_exclusions_agi", period)
        indv_exclusions = person(
            "de_elderly_or_disabled_income_exclusion_joint", period
        )
        net_income = pre_exclusions_agi - indv_exclusions
        joint_income = person.tax_unit.sum(net_income)
        p = parameters(period).gov.states.de.tax.income.subtractions
        if "de_529_plan_subtraction" in p.subtractions:
            # de_pre_exclusions_agi carries each filer's own-column 529
            # subtraction. A joint return instead subtracts the couple's
            # combined contributions up to the joint limit
            # (30 Del. C. § 1106(b)(11)).
            column_529_subtraction = person.tax_unit.sum(
                person("de_529_plan_subtraction", period)
            )
            joint_529_subtraction = person.tax_unit(
                "de_529_plan_subtraction_joint", period
            )
            joint_income += column_529_subtraction - joint_529_subtraction
        joint_net_income = max_(joint_income, 0)
        # allocate any dependent gross income to tax unit head
        is_head = person("is_tax_unit_head", period)
        return joint_net_income * is_head
