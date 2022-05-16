from openfisca_us.model_api import *


class taxable_social_security(Variable):
    value_type = float
    entity = Person
    label = "Taxable Social Security"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        # The taxable amount of Social Security is decided at the tax unit level, but
        # gross income (which contains taxable SS) is person-level. Therefore, we include the
        # taxable SS in gross income by assigning it to the head of the tax unit: this will be
        # not affect overall tax liability.

        is_tax_unit_head = person("is_tax_unit_head", period)
        tax_unit_taxable_uc = person.tax_unit(
            "tax_unit_taxable_social_security", period
        )
        return is_tax_unit_head * tax_unit_taxable_uc
