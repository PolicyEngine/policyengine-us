from policyengine_us.model_api import *


class social_security_worker_computation_year(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = "Supplied Social Security worker computation year"
    documentation = "Authoritative underlying-record eligibility/computation year for linked COLA exposure, with zero indicating unavailable. Supply the legally applicable record basis; this input does not infer disability or deceased-worker computation history."
