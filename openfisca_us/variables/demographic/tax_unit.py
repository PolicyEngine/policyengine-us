from openfisca_core.model_api import *
from openfisca_us.entities import *


class tax_unit_id(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Unique reference for this tax unit"
    definition_period = ETERNITY


class tax_unit_weight(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Tax unit weight"
    definition_period = YEAR


class person_tax_unit_id(Variable):
    value_type = int
    entity = Person
    label = u"Unique reference for the tax unit of this person"
    definition_period = ETERNITY


class MARSType(Enum):
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"
    HOUSEHOLD_HEAD = "Head of household"
    WIDOW = "Widow(er)"


class is_tax_unit_head(Variable):
    value_type = bool
    entity = Person
    label = "Head of tax unit"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        # Use order of input (first)
        return person.tax_unit.members_position == 0


class is_tax_unit_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Spouse of tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        # Use order of input (second)
        return person.tax_unit.members_position == 1


class is_tax_unit_dependent(Variable):
    value_type = bool
    entity = Person
    label = u"Is a dependent in the tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        return not_(
            person("is_tax_unit_head", period)
            + person("is_tax_unit_spouse", period)
        )
