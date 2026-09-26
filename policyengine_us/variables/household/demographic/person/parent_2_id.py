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
        "together and among tax unit members for the claimed-by-parent test; "
        "an id that resolves to neither is an absent parent, which still "
        "identifies siblings. Because 0 means unknown, real person ids must be "
        "nonzero, and the default person_id starts at 0, so supply person_id "
        "with parent ids. Ids are compared after int32 storage, so every "
        "member of a household and of a tax unit needs a distinct nonzero "
        "int32 person_id."
    )
