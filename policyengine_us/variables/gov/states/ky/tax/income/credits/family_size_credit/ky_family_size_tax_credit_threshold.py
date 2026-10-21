from policyengine_us.model_api import *


class ky_family_size_tax_credit_threshold(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky family size tax credit threshold amount"
    unit = USD
    documentation = (
        "The federal poverty guideline for the tax unit's family size, counting "
        "no more than four people. The family size tax credit rate depends on "
        "modified gross income as a share of this amount."
    )
    definition_period = YEAR
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188"

    def formula(tax_unit, period, parameters):
        fpg = parameters(period).gov.hhs.fpg
        # This will be CONTIGUOUS_US for Kentucky.
        state_group = tax_unit.household("state_group_str", period)
        p1 = fpg.first_person[state_group]
        padd = fpg.additional_person[state_group]
        family_size = tax_unit("tax_unit_size", period)
        # No more than 4 people are accounted for in the credit
        p = parameters(period).gov.states.ky.tax.income.credits.family_size
        capped_family_size = min_(family_size, p.family_size_cap)
        return p1 + padd * (capped_family_size - 1)
