from openfisca_us.model_api import *


class separate_filer_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Separate filer itemizes"
    documentation = "Whether the taxpayer in this tax unit has a spouse who files separately and itemizes deductions."
