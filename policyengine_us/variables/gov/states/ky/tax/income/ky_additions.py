from policyengine_us.model_api import *


class ky_additions(Variable):
    value_type = float
    entity = Person
    label = "Kentucky additions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53498",
        "https://revenue.ky.gov/Forms/Schedule%20M%202022.pdf#page=1",
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=23",
        "https://revenue.ky.gov/Forms/Schedule%20M-2021.pdf#page=1",
        "https://taxsim.nber.org/historical_state_tax_forms/KY/2021/Form%20740%20Packet%20Instructions-2021.pdf#page=27",
        # 2020 Form 740 instructions, Schedule M line 5: contributions
        # claimed on federal Form 1040 line 10b.
        "https://revenue.ky.gov/Forms/740%20Instructions%20Packet%205.7.21.pdf#page=27",
    )
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        # The 2020 federal charitable deduction for non-itemizers is added
        # back in the part of it that adjusted_gross_income_person (and so
        # ky_federal_agi) deducts from each filer.
        return person("charitable_contributions_ald_person", period)
