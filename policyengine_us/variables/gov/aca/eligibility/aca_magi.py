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
        "medicaid_magi without the tax-exempt interest and Social Security "
        "of the return's dependents who are outside the tax family "
        "(is_aca_tax_family_member), which happens only on a return whose "
        "head or spouse can be claimed elsewhere. medicaid_magi adds those "
        "two amounts for every member (tax unit AGI already leaves "
        "dependents' income out); both are nonnegative, so removing them "
        "after medicaid_magi's zero floor gives the same result as removing "
        "them before it."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        outside_family = ~filer & ~person("is_aca_tax_family_member", period)
        excluded = tax_unit.sum(
            outside_family
            * (
                person("tax_exempt_interest_income", period)
                + person("social_security", period)
            )
        )
        return max_(0, tax_unit("medicaid_magi", period) - excluded)
