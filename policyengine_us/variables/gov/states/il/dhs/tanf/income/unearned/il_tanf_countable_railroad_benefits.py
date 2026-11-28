from policyengine_us.model_api import *


class il_tanf_countable_railroad_benefits(Variable):
    value_type = float
    entity = Person
    label = "Illinois TANF countable railroad retirement benefits"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = "https://idjj.illinois.gov/content/dam/soi/en/web/idjj/documents/register-volume45-issue-29.pdf#page=419"

    def formula(person, period, parameters):
        railroad = max_(person("railroad_benefits", period), 0)
        disability = max_(person("railroad_disability_benefits", period), 0)
        ssi_payment_level = parameters(period).gov.ssa.ssi.amount.individual
        disability_disregard = min_(min_(disability, railroad), ssi_payment_level)
        return railroad - disability_disregard
