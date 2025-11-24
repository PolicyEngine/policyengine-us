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
        assistance_unit_size = spm_unit("mo_tanf_assistance_unit_size", period)

        # For household sizes 1-base_table_max_size, use the table
        # For sizes > max, use the max table size as base
        max_table_size = p.base_table_max_size
        table_size = min_(assistance_unit_size, max_table_size)
        base_amount = p.amount[table_size]

        # For household sizes > base_table_max_size, add increment for each additional person
        additional_persons = max_(assistance_unit_size - max_table_size, 0)
        additional_amount = additional_persons * p.additional_person_increment

        return base_amount + additional_amount
