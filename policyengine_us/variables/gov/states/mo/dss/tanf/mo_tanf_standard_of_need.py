from policyengine_us.model_api import *


class mo_tanf_standard_of_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF Standard of Need amount"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-05-185/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf.standard_of_need
        size = spm_unit("spm_unit_size", period)
        table_size = min_(size, p.base_table_max_size)
        base_amount = p.amount[table_size]
        additional_persons = max_(size - p.base_table_max_size, 0)
        additional = additional_persons * p.additional_person_increment
        return base_amount + additional
