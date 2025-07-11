from policyengine_us.model_api import *


class dc_liheap_income_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Income level for DC LIHEAP payment"
    definition_period = YEAR
    reference = "https://doee.dc.gov/sites/default/files/dc/sites/doee/service_content/attachments/DOEE%20FY24%20LIHEAP_REGULAR_Benefits_Table-Matrix.pdf"
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        p = parameters(period).gov.states.dc.doee.liheap

        levels = [i * p.income_level_increment for i in range(1, 10)]

        return select(
            [income <= level for level in levels],
            list(range(1, 10)),
            default=10,
        )
