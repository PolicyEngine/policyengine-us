from openfisca_us.model_api import *


class taxable_unemployment_insurance(Variable):
    value_type = float
    entity = Person
    label = "Taxable unemployment insurance"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        # The taxable amount of unemployment insurance is decided at the tax unit level, but
        # gross income (which contains taxable UI) is person-level. Therefore, we include the
        # taxable UI in gross income by assigning it to the head of the tax unit: this will be
        # not affect overall tax liability.

        is_tax_unit_head = person("is_tax_unit_head", period)
        tax_unit_taxable_ui = person.tax_unit(
            "tax_unit_taxable_unemployment_insurance", period
        )
        return where(is_tax_unit_head, tax_unit_taxable_ui, 0)
