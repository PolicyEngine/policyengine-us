from policyengine_us.model_api import *


class eitc_child_lived_with_taxpayer_more_than_half_year(Variable):
    value_type = bool
    entity = Person
    label = "Child lived with the EITC filer for more than half the tax year"
    definition_period = YEAR
    default_value = True
    reference = "https://www.law.cornell.edu/uscode/text/26/32#d_2_B_ii"
    documentation = """
    Whether this person resided with the tax unit filer for more than
    half the tax year, including applicable temporary-absence exceptions.
    Defaults to true to preserve the model's existing assumption that
    qualifying child dependents reside with their filer. Set to false
    when the child does not meet the residence-duration test. This input
    alone does not establish that the person is a qualifying child.
    """
