from policyengine_us.model_api import *


class ne_adc_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska ADC standard of need"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=43-513",
        "https://dhhs.ne.gov/Pages/Title-468.aspx",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.adc
        size = spm_unit("spm_unit_size", period.this_year)
        # Parameter table defines sizes 1-10; for larger sizes, add increment per person
        max_table_size = p.max_unit_size
        capped_size = min_(size, max_table_size)
        base_amount = p.benefit.standard_of_need.amount[capped_size]
        additional_persons = max_(size - max_table_size, 0)
        additional_amount = (
            additional_persons * p.benefit.standard_of_need.additional_person
        )
        return base_amount + additional_amount
