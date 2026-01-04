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
        p = parameters(period).gov.states.nd.dhs.tanf.benefit
        person = spm_unit.members

        # Children: dependents who meet TANF demographic eligibility
        is_dependent = person("is_tax_unit_dependent", period)
        is_tanf_eligible = person(
            "is_person_demographic_tanf_eligible", period
        )
        is_child = is_dependent & is_tanf_eligible
        child_count = spm_unit.sum(is_child)

        # Caretakers: head or spouse of tax unit
        is_caretaker = person("is_tax_unit_head_or_spouse", period)
        caretaker_count = spm_unit.sum(is_caretaker)

        # Cap to match 400-19-110-05 table structure (0-2 caretakers, 0-10 children)
        caretaker_count_capped = min_(caretaker_count, 2).astype(int)
        child_count_capped = min_(child_count, p.max_children).astype(int)

        return p.standard_of_need[caretaker_count_capped][child_count_capped]
