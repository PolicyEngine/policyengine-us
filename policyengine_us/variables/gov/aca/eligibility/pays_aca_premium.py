from policyengine_us.model_api import *


class pays_aca_premium(Variable):
    value_type = bool
    entity = Person
    label = "Person pays an ACA marketplace premium"
    definition_period = YEAR

    def formula(person, period, parameters):
        immigration_eligible = person("is_aca_ptc_immigration_status_eligible", period)
        taxpayer_has_tin = person.tax_unit("taxpayer_has_tin", period)
        is_status_eligible = taxpayer_has_tin & immigration_eligible

        p = parameters(period).gov.aca
        is_coverage_eligible = add(person, period, p.ineligible_coverage) == 0
        is_aca_adult = person("age", period) > p.slcsp.max_child_age
        child_pays = person("aca_child_index", period) <= p.max_child_count
        pays_age_based_premium = is_aca_adult | child_pays

        return is_status_eligible & is_coverage_eligible & pays_age_based_premium
