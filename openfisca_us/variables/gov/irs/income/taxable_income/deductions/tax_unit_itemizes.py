from openfisca_us.model_api import *


class tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes tax deductions"
    unit = USD
    documentation = "Whether this tax unit elects to itemize deductions, rather than claim standard deductions."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        tax_if_itemizing = tax_unit("tax_liability_if_itemizing", period)
        tax_if_not_itemizing = tax_unit(
            "tax_liability_if_not_itemizing", period
        )
        return tax_if_itemizing < tax_if_not_itemizing
