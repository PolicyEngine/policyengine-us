from policyengine_us.model_api import *


class pa_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF maximum benefit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf
        household = spm_unit.household

        county_group = household("pa_tanf_county_group", period)
        size = spm_unit("spm_unit_size", period)

        max_size = p.max_family_size_in_table
        capped_size = min_(size, max_size).astype(int)

        benefit = p.family_size_allowance.amount[county_group][capped_size]

        additional_people = max_(size - max_size, 0)
        additional_benefit = (
            additional_people * p.family_size_allowance.additional_person
        )

        return benefit + additional_benefit
