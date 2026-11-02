from policyengine_us.model_api import *


class charitable_contributions_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Above-the-line charitable deduction for non-itemizers for each person"
    unit = USD
    documentation = (
        "Each head's or spouse's part of the tax unit's 2020 above-the-line "
        "charitable deduction (charitable_contributions_ald), in proportion "
        "to their own cash gifts to organizations described in section "
        "170(b)(1)(A), or equally when neither gave. 62(a)(22) counts the "
        "contributions made by the eligible individual. A tax unit "
        "dependent's part is zero."
    )
    definition_period = YEAR
    reference = (
        # CARES Act sec. 2204: 26 U.S.C. 62(a)(22) and 62(f).
        "https://www.congress.gov/116/plaws/publ136/PLAW-116publ136.pdf#page=65",
    )

    def formula(person, period, parameters):
        amount = person.tax_unit("charitable_contributions_ald", period)
        own = person("resolved_charitable_cash_donations_50_pct", period)
        return amount * filer_share(person, period, own)
