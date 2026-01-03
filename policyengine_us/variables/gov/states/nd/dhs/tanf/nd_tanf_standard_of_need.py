from policyengine_us.model_api import *


class nd_tanf_standard_of_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota TANF standard of need"
    unit = USD
    definition_period = MONTH
    reference = "https://www.nd.gov/dhs/policymanuals/40019/400_19_110_05.htm"
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.tanf.benefit.standard_of_need
        person = spm_unit.members
        age = person("age", period.this_year)

        # Count caretakers (adults) and children in the unit
        is_adult = age >= 18
        is_child = age < 18
        caretaker_count = spm_unit.sum(is_adult)
        child_count = spm_unit.sum(is_child)

        # Cap caretakers at 2 and children at 10 to match 400-19-110-05 table structure.
        # Table has 0/1/2 caretakers and 0-10 children; larger families use max values.
        caretaker_count_capped = min_(caretaker_count, 2)
        child_count_capped = min_(child_count, 10)

        # Look up standard of need based on caretaker count and children
        return select(
            [
                caretaker_count_capped == 0,
                caretaker_count_capped == 1,
                caretaker_count_capped == 2,
            ],
            [
                p.caretakers_0.calc(child_count_capped),
                p.caretakers_1.calc(child_count_capped),
                p.caretakers_2.calc(child_count_capped),
            ],
            default=0,
        )
