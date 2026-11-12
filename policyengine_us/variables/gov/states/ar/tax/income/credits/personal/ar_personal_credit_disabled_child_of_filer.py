from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    has_parent_ids,
    tax_unit_parent_indices,
)


class ar_personal_credit_disabled_child_of_filer(Variable):
    value_type = bool
    entity = Person
    label = "Child of a filer by birth or adoption for the Arkansas developmentally disabled credit"
    documentation = (
        "Whether the person is a child of the head or spouse by birth or "
        "adoption, the credit's route that does not need an IRC 152 "
        "dependent. Defaults to whether a parent id names a head or spouse of "
        "the tax unit, and to true when the person has no parent ids (the "
        "relationship is unknown). Parent ids also name step-parents, so set "
        "this to false for a stepchild who is no filer's child by birth or "
        "adoption."
    )
    definition_period = YEAR
    reference = (
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F1999%2FPublic%2FACT417.pdf#page=2",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        filer = person("is_tax_unit_head_or_spouse", period)
        first, second = tax_unit_parent_indices(person, period)
        names_filer = np.where(first >= 0, filer[first], False) | np.where(
            second >= 0, filer[second], False
        )
        return names_filer | ~has_parent_ids(person, period)
