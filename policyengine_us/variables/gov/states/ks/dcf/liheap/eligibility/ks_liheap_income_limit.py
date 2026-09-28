from policyengine_us.model_api import *


class ks_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Kansas LIEAP annualized income limit"
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13360.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13360.htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.eligibility
        size = spm_unit("ks_liheap_household_size", period)
        capped_size = clip(size, 1, p.max_table_size)
        additional_people = max_(size - p.max_table_size, 0)
        monthly_limit = (
            p.income_limit[capped_size]
            + additional_people * p.additional_person_income_limit
        )
        return monthly_limit * MONTHS_IN_YEAR
