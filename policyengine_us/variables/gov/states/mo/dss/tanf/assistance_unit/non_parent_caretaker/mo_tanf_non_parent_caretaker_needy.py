from policyengine_us.model_api import *


class mo_tanf_non_parent_caretaker_needy(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF non-parent caretaker is needy"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-300",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-35/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-40/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-10/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Budgeted per SPM unit, like the rest of mo_tanf. An SPM unit with
        # two tax units that each have a non-parent caretaker pools their
        # budgets; that case is not modeled separately.
        person = spm_unit.members
        npcr = person("mo_tanf_non_parent_caretaker", period)
        member = person("mo_tanf_non_parent_caretaker_budget_member", period)
        spouse = member & ~npcr
        is_ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        # DSS Manual 0210.005.35: "when the NPCR's spouse does not live in
        # the home or the NPCR's spouse is an SSI or SSI-SP recipient,
        # consider the NPCR needy without completing the budget". SSI-SP
        # receipt is not observable apart from SSI.
        spouse_in_home = spm_unit.any(spouse)
        spouse_receives_ssi = spm_unit.any(spouse & is_ssi_recipient)
        automatically_needy = ~spouse_in_home | spouse_receives_ssi
        # Otherwise the budget compares the group's income with the full
        # standard of need for the group's size: "If this budget shows
        # need, the NPCR is determined to be needy." Refusal of the spouse
        # to cooperate (which makes the NPCR not needy) is not modeled.
        p = parameters(period).gov.states.mo.dss.tanf.standard_of_need
        size = spm_unit.sum(member).astype(int)
        table_size = max_(min_(size, p.base_table_max_size), 1)
        additional_persons = max_(size - p.base_table_max_size, 0)
        standard = (
            p.amount[table_size] + additional_persons * p.additional_person_increment
        )
        income = spm_unit("mo_tanf_non_parent_caretaker_countable_income", period)
        budget_shows_need = income < standard
        return spm_unit.any(npcr) & (automatically_needy | budget_shows_need)
