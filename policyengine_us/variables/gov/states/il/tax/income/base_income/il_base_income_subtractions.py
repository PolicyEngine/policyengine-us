from policyengine_us.model_api import *


class il_base_income_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL base income subtractions"
    unit = USD
    definition_period = YEAR
    reference = (
        # 35 ILCS 5/203(a)(2)(F), (H) and (L) subtract amounts included in
        # the taxpayer's federal adjusted gross income.
        "https://www.ilga.gov/Documents/legislation/ilcs/documents/003500050K203.htm",
        "https://tax.illinois.gov/content/dam/soi/en/web/tax/forms/incometax/documents/currentyear/individual/il-1040-instr.pdf#page=7",
        "https://tax.illinois.gov/content/dam/soi/en/web/tax/research/publications/pubs/documents/pub-120.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.base
        # Illinois subtracts only amounts included in federal AGI (IL-1040,
        # Line 1). Dependents' income is not in the filer's federal AGI; they
        # report it on their own return, so only the head's and spouse's
        # person-level amounts count.
        total_subtractions = tax_unit_non_dep_add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
