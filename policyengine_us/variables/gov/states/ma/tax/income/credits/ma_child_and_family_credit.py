from policyengine_us.model_api import *


class ma_child_and_family_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts child and family tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/massachusetts-child-and-family-tax-credit"
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.credits.child_and_family
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        child = age < p.child_age_limit
        elderly = age >= p.elderly_age_limit
        disabled = person("is_disabled", period)
        eligible_dependent = dependent & (child | elderly | disabled)
        count_eligible_dependents = tax_unit.sum(eligible_dependent)
        # A disabled spouse is a qualifying individual under
        # IRC Section 21(b)(1)(C), incorporated by M.G.L. c. 62
        # Section 6(x)(ii) since 2023. On a joint return there is no legal
        # "primary" taxpayer, so either joint filer who is incapable of
        # self-care is "the spouse of the taxpayer"; we key on
        # is_tax_unit_head_or_spouse rather than is_tax_unit_spouse to avoid
        # a head/spouse ordering (age) artifact. The credit is restricted to
        # joint returns (IRC Section 21(e)(2)), excluding the unmarried
        # sole-filer case.
        # Modeling note: the generic is_disabled input proxies the IRC
        # Section 21 "incapable of self-care" and same-principal-abode tests,
        # and the 2024+ noncustodial-parent rule (Section 21 applied without
        # subsection (e)(5)) is not modeled.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        filing_status = tax_unit("ma_filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        disabled_head_or_spouse = head_or_spouse & disabled
        # IRC Section 21(b)(1)(C) recognizes a single "spouse of the
        # taxpayer" qualifying individual, so a both-disabled joint couple
        # counts as one qualifying individual, not two.
        has_disabled_spouse = (
            p.disabled_spouse_eligible
            & joint
            & (tax_unit.sum(disabled_head_or_spouse) > 0)
        )
        count_eligible = count_eligible_dependents + has_disabled_spouse
        capped_eligible = min_(count_eligible, p.dependent_cap)
        # Married taxpayers filing separately cannot claim the credit.
        separate = filing_status == filing_status.possible_values.SEPARATE
        return ~separate * capped_eligible * p.amount
