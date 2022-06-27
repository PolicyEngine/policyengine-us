from openfisca_us.model_api import *


class in_qualifying_child_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "IN qualifying depdendent child count"
    unit = USD
    documentation = "Number of qualifying children for the IN additional exemption."
    definition_period = YEAR

    formula = sum_of_variables(["in_is_qualifying_dependent_child"])