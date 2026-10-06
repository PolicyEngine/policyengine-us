from policyengine_us.model_api import *


class parent_2_id(Variable):
    value_type = int
    entity = Person
    label = "Second parent's person ID"
    definition_period = YEAR
    default_value = 0
    documentation = (
        "person_id of one of this person's parents, 0 when unknown. Name "
        "natural, adoptive and step parents alike: 42 CFR 435.603(b) defines "
        "parents, children and siblings to include step relatives, and CPS "
        "PEPAR1 and PEPAR2 name a co-resident parent of any type. An id "
        "resolves among household members for rules that require living "
        "together and, for the claimed-by-parent test, among the members of "
        "the claiming tax unit: the person's own, or a known claiming tax "
        "unit elsewhere. An id that names a co-resident resolves to that "
        "co-resident. An id that resolves to no one is an absent parent, "
        "which still identifies siblings. When the ids name exactly one "
        "parent the person lives with, Medicaid MAGI rules also treat that "
        "parent's co-resident spouse, shown by a joint return or by a "
        "two-person marital unit with the cohabiting-spouses flag, as a step "
        "parent. Because 0 means unknown, real person ids must be nonzero, "
        "and the default person_id starts at 0, so supply person_id with "
        "parent ids. Ids are compared after int32 storage. Every member of a "
        "household and of a tax unit needs a distinct nonzero int32 "
        "person_id, and when any tax unit spans households or any "
        "medicaid_claiming_tax_unit_id is set, person ids must be distinct "
        "across the whole simulation. An id that matches two members of one "
        "household or tax unit breaks this contract and resolves to neither."
    )
