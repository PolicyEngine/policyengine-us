from policyengine_us.model_api import *


class social_security_dependents_worker_benefit_ratio(Variable):
    value_type = float
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents composite worker-benefit ratio"
    documentation = "Supplied positive composite ratio of this recipient benefit to the underlying worker PIA, including the worker claiming adjustment and all applicable recipient share reductions. The baseline inversion divides by this composite once. Zero means unavailable. Requires an identified worker basis and the separate worker_ratio_identified assertion; no uprating."
