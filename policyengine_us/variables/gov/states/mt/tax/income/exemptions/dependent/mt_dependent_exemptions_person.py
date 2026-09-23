from policyengine_us.model_api import *


class mt_dependent_exemptions_person(Variable):
    value_type = int
    entity = Person
    label = "Montana dependent exemption for each dependent"
    unit = USD
    definition_period = YEAR
    reference = "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-403/"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions

        if p.applies:
            # A qualifying child under IRC 152(c) is a dependent regardless of
            # income. Any other dependent counts only if their gross income
            # does not exceed the exemption amount (Form 2 instructions: a
            # dependent is an individual "who does not have gross income of
            # more than" the exemption amount "unless the dependent is a
            # 'qualifying child' according to the federal rules").
            qualifying_child = person("is_qualifying_child_dependent", period)
            dependent = person("is_tax_unit_dependent", period)
            gross_income = person("irs_gross_income", period)
            other_dependent = dependent & ~qualifying_child & (gross_income <= p.amount)
            # Disabled children get an additional exemption.
            disabled = person("is_disabled", period)

            eligible_dependent = qualifying_child * (1 + disabled) + other_dependent
            return eligible_dependent * p.amount

        return 0
