from policyengine_us.model_api import *


class ky_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Kentucky LIHEAP regular heating eligibility"
    defined_for = StateCode.KY
    reference = (
        # Sections 2(1)(d), 2(2), 3(2) and 8(3).
        "https://apps.legislature.ky.gov/law/kar/titles/921/004/116/",
        # Sections 17.2-17.3 (pages 33-34).
        "https://liheapch.acf.gov/docs/2026/state-plans/KY_Plan_2026.pdf#page=33",
    )

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ky_liheap_income_eligible", period)
        # 921 KAR 4:116 Section 3(2): the household pays for home heating
        # directly or as an undesignated portion of the rent.
        responsible = (spm_unit("heating_expense", period) > 0) | spm_unit(
            "heat_expense_included_in_rent", period
        )
        # LIHEAP is a federal public benefit, so at least one member must be a
        # citizen or qualified noncitizen; plan Section 17.3 verifies that
        # status.
        has_qualified_member = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        # 921 KAR 4:116 Section 2(1)(d) requires "a Social Security number, or
        # a permanent residency card, for each household member". Section 2(2)
        # treats the application as incomplete until it is received and
        # Section 8(3) denies it after five working days, so a household with
        # a member who has neither is ineligible. The plan's Section 17.2
        # checklist requires the card from adults and requests it from other
        # members; the regulation's per-member rule applies here. Section 1(10)
        # defines the household with no immigration carve-out, so every member
        # counts for size and income.
        person = spm_unit.members
        ssn_card_type = person("ssn_card_type", period)
        immigration_status = person("immigration_status", period)
        has_ssn = ssn_card_type != ssn_card_type.possible_values.NONE
        is_permanent_resident = (
            immigration_status
            == immigration_status.possible_values.LEGAL_PERMANENT_RESIDENT
        )
        all_documented = spm_unit.all(has_ssn | is_permanent_resident)
        return income_eligible & responsible & has_qualified_member & all_documented
