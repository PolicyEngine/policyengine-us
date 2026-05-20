from policyengine_us.model_api import *


class md_ccs_weekly_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Maryland Child Care Scholarship (CCS) weekly copayment"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.12",
        "https://mgaleg.maryland.gov/2024RS/Chapters_noln/CH_717_sb0362E.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.msde.ccs.copay

        # TCA/SSI recipients pay $0 copayment per COMAR 13A.14.06.12A(1).
        # We don't track TANF applicants separately from recipients at the
        # moment; the regulation covers both.
        is_tca = spm_unit("is_tanf_enrolled", period)
        receives_ssi = add(spm_unit, period, ["ssi"]) > 0

        # SNAP/WIC recipients have copayments waived per Chapter 525 of 2022 (HB 995).
        is_snap = add(spm_unit, period, ["snap"]) > 0
        receives_wic = add(spm_unit, period, ["wic"]) > 0
        exempt = is_tca | receives_ssi | is_snap | receives_wic

        # Weekly copay per child based on service unit (enum-keyed lookup)
        person = spm_unit.members
        service_unit = person("md_ccs_service_unit", period)
        weekly_per_child = p.weekly_amount[service_unit]

        # Only charge copay for eligible children
        is_eligible_child = person("md_ccs_eligible_child", period)
        weekly_per_child = where(is_eligible_child, weekly_per_child, 0)

        # Copay assessed for up to max_children_with_copay children.
        # We don't track the COMAR youngest/2nd/3rd-child rank distinction at
        # the moment — moot under the flat $1/$2/$3 schedule, where every child
        # at the same service unit pays the same amount.
        eligible_child_count = add(spm_unit, period, ["md_ccs_eligible_child"])
        capped_count = min_(eligible_child_count, p.max_children_with_copay)
        total_weekly = spm_unit.sum(weekly_per_child)
        scale = where(
            eligible_child_count > 0,
            capped_count / eligible_child_count,
            0,
        )
        scaled_weekly = total_weekly * scale

        # Federal cap: copay cannot exceed 7% of gross income per 45 CFR 98.45(k)
        countable_income = spm_unit("md_ccs_countable_income", period)
        weekly_income = countable_income * MONTHS_IN_YEAR / WEEKS_IN_YEAR
        federal_cap = weekly_income * p.federal_cap_rate

        return where(exempt, 0, min_(scaled_weekly, federal_cap))
