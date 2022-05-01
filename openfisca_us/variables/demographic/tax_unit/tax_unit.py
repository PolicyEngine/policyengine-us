from openfisca_us.model_api import *


class dsi(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Dependent elsewhere"
    documentation = "Claimed as dependent in another tax unit"


class midr(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Separate filer itemizes"
    documentation = (
        "True if separately-filing spouse itemizes, otherwise false"
    )


class xtot(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Filing unit exemptions"
    documentation = "Total number of exemptions for filing unit"


class age_head(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Age of head of tax unit"
    documentation = "Age in years of taxpayer (i.e. primary adult)"
    unit = "year"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        head = person("is_tax_unit_head", period)
        return tax_unit.max(age * head)


class age_spouse(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Age of spouse of tax unit"
    documentation = "Age in years of spouse (i.e. secondary adult if present)"
    unit = "year"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        spouse = person("is_tax_unit_spouse", period)
        return tax_unit.max(age * spouse)


class blind_head(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit head is blind"
    documentation = "True if taxpayer is blind; otherwise False"


class blind_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit spouse is blind"
    documentation = "1 if spouse is blind; otherwise 0"


class num(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "2 when MARS is 2 (married filing jointly); otherwise 1"
    unit = USD
