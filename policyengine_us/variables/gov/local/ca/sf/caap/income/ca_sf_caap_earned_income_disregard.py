from policyengine_us.model_api import *


class ca_sf_caap_earned_income_disregard(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "San Francisco County CAAP earned income disregard per person"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.sf.caap
        earned = person("ca_sf_caap_earned_income", period)
        # The 5-tier marginal disregard ($200 + 2/3 of next $150 + 1/2 + 1/3 +
        # 1/5, remainder dollar-for-dollar) applies only to current recipients;
        # new applicants receive no disregard (SEC. 20.7-21(j) / Div 94-14).
        is_recipient = person.spm_unit("ca_sf_caap_is_recipient", period.this_year)
        disregard = p.earned_income_disregard.calc(earned)
        return where(is_recipient, disregard, 0)
