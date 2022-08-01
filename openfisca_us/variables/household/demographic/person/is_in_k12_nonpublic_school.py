from openfisca_us.model_api import *


class is_in_k12_nonpublic_school(Variable):
    value_type = bool
    entity = Person
    label = "Is in a K-12 nonpublic school fulltime"
    definition_period = YEAR
