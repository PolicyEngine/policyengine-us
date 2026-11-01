from policyengine_us.model_api import *


class ca_calworks_child_care_payment_factor(Variable):
    value_type = float
    entity = Person
    label = "California CalWORKs Child Care payment factor"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/child-care/regional-market-rate-ceilings.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.child_care.rate_ceilings
        factor_category = person("ca_calworks_child_care_factor_category", period)
        factor_categories = factor_category.possible_values
        return select(
            [
                factor_category == factor_categories.EVENING_AND_WEEKEND_I,
                factor_category == factor_categories.EVENING_AND_WEEKEND_II,
                factor_category == factor_categories.EXCEPTIONAL_NEEDS,
                factor_category == factor_categories.SEVERELY_DISABLED,
            ],
            [
                p.evening_or_weekend_I,
                p.evening_or_weekend_II,
                p.exceptional_needs,
                p.severely_disabled,
            ],
            default=1,
        )
