from policyengine_us.model_api import *


class dc_ccsp_second_child_copay(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "DC Child Care Subsidy Program (CCSP) second child copay amount"
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/Sliding%20Fee%20Scale.pdf"
    definition_period = MONTH
    defined_for = "dc_ccsp_is_second_youngest_child"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.copay.second_child
        countable_income = person.spm_unit("dc_ccsp_countable_income", period)
        fpg = person.spm_unit("spm_unit_fpg", period)
        income_to_fpg_ratio = countable_income / fpg

        is_full_time = person("dc_ccsp_is_full_time", period)
        copay_per_day = where(
            is_full_time,
            p.full_time.calc(income_to_fpg_ratio),
            p.part_time.calc(income_to_fpg_ratio),
        )
        attending_days_per_month = person(
            "dc_ccsp_attending_days_per_month", period
        )
        return copay_per_day * attending_days_per_month
