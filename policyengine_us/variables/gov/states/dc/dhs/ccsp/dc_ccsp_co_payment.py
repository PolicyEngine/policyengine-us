from policyengine_us.model_api import *


class dc_ccsp_co_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Child Care Subsidy Program (CCSP) co-payment"
    definition_period = MONTH
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=28"
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.co_payment
        qualified_need_eligible = spm_unit(
            "dc_ccsp_qualified_need_eligible", period
        )
        countable_income = spm_unit("dc_ccsp_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        income_eligible = countable_income < fpg * p.exempted_rate
        exempted_eligible = qualified_need_eligible | income_eligible
        # Check number of eligible child, and their full / part time status
        person = spm_unit.members
        full_time = person("dc_ccsp_is_full_time_child_care", period)
        first_child_co_payment = where(
            full_time,
            p.first_child.full_time.calc(countable_income),
            p.first_child.part_time.calc(countable_income),
        )
        second_child_co_payment = where(
            full_time,
            p.second_child.full_time.calc(countable_income),
            p.second_child.part_time.calc(countable_income),
        )
        have_second_child = (
            add(spm_unit, period, ["dc_ccsp_eligible_child"]) > 1
        )
        total_co_payment = where(
            have_second_child,
            first_child_co_payment + second_child_co_payment,
            first_child_co_payment,
        )

        return where(exempted_eligible, 0, total_co_payment)
