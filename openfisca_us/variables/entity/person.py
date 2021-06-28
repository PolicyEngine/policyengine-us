from openfisca_core.model_api import *
from openfisca_us.entities import *

class age(Variable):
    value_type = int
    entity = Person
    label = u'Age of the person in years'
    definition_period = YEAR