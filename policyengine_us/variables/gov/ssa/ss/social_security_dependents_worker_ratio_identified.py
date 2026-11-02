from policyengine_us.model_api import *


class social_security_dependents_worker_ratio_identified(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents worker ratio identified"
    documentation = "Assert that the supplied composite worker-benefit ratio identifies a single underlying worker PIA, including all reductions and credits, with no unaccounted dual entitlement, binding family cap, or earnings-test withholding. False leaves this auxiliary amount unmodeled for the population PIA-ratio lever."
