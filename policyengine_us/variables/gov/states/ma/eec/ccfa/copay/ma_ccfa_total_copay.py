from policyengine_us.model_api import *


class ma_ccfa_total_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Massachusetts Child Care Financial Assistance (CCFA) parent total copay"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=76"

    def formula(spm_unit, period, parameters):
        # TAFDC recipients get free child care (no copay)
        tafdc_eligible = spm_unit("ma_tafdc_eligible", period)

        p = parameters(period).gov.states.ma.eec.ccfa.copay.ratio
        base_copay = spm_unit("ma_ccfa_base_copay", period)
        person = spm_unit.members
        eligible_child = person("ma_ccfa_eligible_child", period)
        age = person("monthly_age", period)
        rank = person.get_rank(spm_unit, age, eligible_child)
        sibling_ratio = select(
            [rank == 0, rank == 1],
            [p.first_child, p.second_child],
            default=p.additional_child,
        )
        ccfa = parameters(period).gov.states.ma.eec.ccfa
        part_time = person("ma_ccfa_has_part_time_authorization", period)
        time_ratio = where(part_time, ccfa.copay.part_time_multiplier, 1)
        total_copay = base_copay * spm_unit.sum(
            eligible_child * sibling_ratio * time_ratio
        )

        exempt = tafdc_eligible
        if ccfa.income.countable_income.person_rules_in_effect:
            exempt = exempt | spm_unit(
                "ma_ccfa_is_nonparent_caregiver_family", period.this_year
            )
        if ccfa.homeless_income_and_copay_exempt:
            exempt = exempt | spm_unit.household("is_homeless", period.this_year)
        return where(exempt, 0, total_copay)
