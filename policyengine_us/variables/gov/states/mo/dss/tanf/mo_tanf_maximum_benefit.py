from policyengine_us.model_api import *


class mo_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF maximum benefit amount"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-15/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf.maximum_benefit
        size = spm_unit("mo_tanf_assistance_unit_size", period)
        # Missouri pays the whole-dollar row in 13 CSR 40-2.310(13).
        table_size = max_(min_(size, p.base_table_max_size), 1)
        base_amount = p.amount[table_size]
        additional_persons = max_(size - p.base_table_max_size, 0)
        return base_amount + additional_persons * p.additional_person_increment
