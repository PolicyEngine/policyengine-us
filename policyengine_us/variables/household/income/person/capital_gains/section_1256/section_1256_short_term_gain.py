from policyengine_us.model_api import *


class section_1256_short_term_gain(Variable):
    value_type = float
    entity = Person
    label = "Short-term part of section 1256 contract gain or loss"
    documentation = "Section 1256(a)(3): 60% of the marked-to-market net gain or loss is long-term and 40% short-term."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1256#a_3"

    def formula(person, period, parameters):
        share = parameters(period).gov.irs.capital_gains.section_1256.long_term_share
        net = person("section_1256_net_gain", period)
        return net * (1 - share)
