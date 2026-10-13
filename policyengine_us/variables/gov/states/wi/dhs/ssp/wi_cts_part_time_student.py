from policyengine_us.model_api import *


class wi_cts_part_time_student(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS child attends school part time"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=31"
