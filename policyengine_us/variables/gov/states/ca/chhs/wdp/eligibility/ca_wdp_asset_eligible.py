from policyengine_us.model_api import *


class ca_wdp_asset_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California 250 Percent Working Disabled Program asset eligible"
    definition_period = YEAR
    reference = "https://www.dhcs.ca.gov/services/working-disabled-program/"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.chhs.wdp.eligibility.asset
        countable_resources = person.tax_unit.sum(
            person("ssi_countable_resources", period)
        )
        tax_unit_size = person.tax_unit("tax_unit_size", period)
        capped_size = min_(tax_unit_size, p.max_people)
        asset_limit = p.base + max_(capped_size - 1, 0) * p.additional_person
        return countable_resources <= asset_limit
