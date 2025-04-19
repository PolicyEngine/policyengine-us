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
            # Qualifying child under IRC 152(c), which defines for the EITC
            qualifying_child = person("is_child_dependent", period)
            # Disabled dependents get an additional exemption.
            disabled = person("is_disabled", period)

            eligible_dependent = qualifying_child * (1 + disabled)
            return eligible_dependent * p.amount

        return 0
