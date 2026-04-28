from policyengine_us.model_api import *


class has_american_opportunity_credit_1098_t_or_exception(Variable):
    value_type = bool
    entity = Person
    label = "Has Form 1098-T or an AOTC exception"
    documentation = "Whether the student received Form 1098-T or meets an exception allowing the American Opportunity Credit to be claimed with substantiated qualified expenses."
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"
