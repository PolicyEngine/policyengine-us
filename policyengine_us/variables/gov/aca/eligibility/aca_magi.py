from policyengine_us.model_api import *


class aca_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA-related modified AGI for this tax unit"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#d_2",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-1#e_1",
    )
    documentation = (
        "Household income for the premium tax credit (IRC 36B(d)(2), 26 CFR "
        "1.36B-1(e)(1)): the taxpayer's modified AGI, both spouses' on a "
        "joint return, plus that of other members of the tax family. It is "
        "medicaid_magi's AGI plus MAGI additions, without the tax-exempt "
        "interest and Social Security of the return's dependents who are "
        "outside the tax family (is_aca_tax_family_member), floored at zero "
        "once. Those amounts are left out only on a return whose head or "
        "spouse can be claimed elsewhere (or, in a tax unit with neither, "
        "whose inferred filer can be); otherwise this equals medicaid_magi. "
        "Tax unit AGI already leaves dependents' income out."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        files_return = person("is_aca_filer", period)
        outside_family = ~files_return & ~person("is_aca_tax_family_member", period)
        needs_exclusion = tax_unit.any(outside_family)
        medicaid_magi = tax_unit("medicaid_magi", period)
        if not needs_exclusion.any():
            return medicaid_magi
        excluded = tax_unit.sum(
            outside_family
            * (
                person("tax_exempt_interest_income", period)
                + person("social_security", period)
            )
        )
        # medicaid_magi's AGI plus additions, before its zero floor, so a
        # negative excluded amount is removed before the floor too.
        additions = parameters(period).gov.hhs.medicaid.income.modification
        unfloored = tax_unit("adjusted_gross_income", period) + add(
            tax_unit, period, additions
        )
        # Keep supplied Medicaid MAGI when no dependent is excluded. Only
        # reconstruct the unfloored amount when removing family income.
        return where(
            needs_exclusion,
            max_(0, unfloored - excluded),
            medicaid_magi,
        )
