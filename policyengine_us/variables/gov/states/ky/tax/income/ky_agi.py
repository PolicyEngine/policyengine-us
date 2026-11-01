from policyengine_us.model_api import *


class ky_agi(Variable):
    value_type = float
    entity = Person
    label = "Kentucky adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11",
        # 2020 Form 740 instructions, Schedule M line 5: contributions
        # claimed on federal Form 1040 line 10b are added back.
        "https://revenue.ky.gov/Forms/740%20Instructions%20Packet%205.7.21.pdf#page=27",
    )
    defined_for = StateCode.KY

    adds = [
        "ky_additions",
        "ky_federal_agi",
        # Schedule M line 5 (2020): the federal charitable deduction for
        # non-itemizers, in the part ky_federal_agi deducts from each filer.
        "charitable_contributions_ald_person",
    ]
    subtracts = ["ky_subtractions"]
