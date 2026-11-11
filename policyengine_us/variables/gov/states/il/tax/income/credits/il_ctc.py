from policyengine_us.model_api import *


class il_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        # 35 ILCS 5/244(a), (d): a taxpayer with a "qualifying child" (IRC 152
        # meaning) under 12 gets a share of the Section 212 credit.
        "https://www.ilga.gov/Documents/legislation/ilcs/documents/003500050K244.htm",
        # 2026 Schedule IL-E/EITC draft instructions: "at least one qualifying
        # child that is under the age of 12".
        "https://tax.illinois.gov/content/dam/soi/en/web/tax/taxprofessionals/draft-forms/documents/iit-draft-forms/2026-iit-vendor-forms-and-instructions/2026-sch-il-e-eitc-instr-vendor.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.credits.ctc
        person = tax_unit.members
        age = person("age", period)
        # 35 ILCS 5/244(d) gives "qualifying child" its IRC 152 meaning, not
        # an allowable dependent, so a filer who can be claimed as a dependent
        # elsewhere still counts their own qualifying child.
        qualifying_child = person("is_qualifying_child_dependent", period)
        eligible_child = qualifying_child & (age < p.age_limit)
        eligible_child_present = tax_unit.any(eligible_child)
        state_eitc = tax_unit("il_eitc", period)
        return eligible_child_present * state_eitc * p.rate
