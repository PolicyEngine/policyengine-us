from openfisca_us.model_api import *


class ssi_deemed_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income deemed income"
    label = "SSI deemed income"
    unit = USD
    reference = "https://ncler.acl.gov/NCLER/media/NCLER/documents/SSI-Deeming-Chapter-Summary.pdf"
