from policyengine_us.model_api import *


class unemployment_compensation_start_month(Variable):
    value_type = int
    entity = Person
    label = "Calendar month unemployment compensation receipt starts"
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Calendar month (1 = January, 12 = December) in which the person's "
        "block of unemployment_compensation_months starts. Survey microdata "
        "report weeks unemployed but not the months they fall in, so the "
        "dataset build assigns every person a start month and stores it "
        "here; the model itself draws nothing (policyengine-core#500). The "
        "assignment is an allocation device, not observed timing. 0 means "
        "not supplied: in a household situation the start month then "
        "follows the person's position in their household (see "
        "is_receiving_unemployment_compensation). The value is not uprated, "
        "so a person keeps the same start month in every year."
    )
    reference = "https://www.law.cornell.edu/cfr/text/7/273.7#b_1_v"
