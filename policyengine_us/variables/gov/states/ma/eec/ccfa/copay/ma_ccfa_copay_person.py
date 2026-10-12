from policyengine_us.model_api import *


class ma_ccfa_copay_person(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Massachusetts CCFA child copay before family exemptions"
    defined_for = StateCode.MA
    unit = USD
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=76",
        "https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=46",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.copay
        spm_unit = person.spm_unit
        # As in VA CCSP, only children actually attending care incur fees.
        attending = person("childcare_attending_days_per_month", period.this_year) > 0
        participating = person("ma_ccfa_eligible_child", period) & attending
        age = person("age", period.this_year)
        rank = person.get_rank(spm_unit, age, participating)
        ratio = select(
            [rank == 0, rank == 1],
            [p.ratio.first_child, p.ratio.second_child],
            default=p.ratio.additional_child,
        )
        part_time = person("ma_ccfa_is_part_time_care", period)
        fee = (
            spm_unit("ma_ccfa_base_copay", period)
            * ratio
            * where(part_time, p.part_time_ratio, 1)
        )
        fee = min_(fee, person("ma_ccfa_maximum_reimbursement", period))
        return where(participating, max_(fee, 0), 0)
