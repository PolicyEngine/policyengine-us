from policyengine_us.model_api import *


class ma_child_and_family_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts child and family tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/massachusetts-child-and-family-tax-credit",
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section6",
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
        # IRC Section 21(b)(1)(B), via M.G.L. c. 62 Section 6(x)(ii): a
        # dependent physically or mentally incapable of self-care qualifies
        # at any age, alongside the Section 6(x)(iii) disabled-dependent
        # category.
        # Keep BOTH the dependent is_disabled route and the
        # is_incapable_of_self_care route: the mass.gov CFTC page collapses
        # category (3) into the self-care test, but c.62 Section 6(x) and
        # Form 1 keep the disabled-dependent and self-care-incapable
        # categories legally distinct (disability is broader than the
        # self-care standard), so do not "fix" this toward the web page by
        # dropping is_disabled. The asymmetry with the spouse route below is
        # deliberate: Section 21(b)(1)(C) recognizes only a self-care-
        # incapable spouse, not a merely disabled one.
        # is_incapable_of_self_care is a bare Person boolean input. Microcosm
        # populates it from the ASEC self-care difficulty item PEDISDRS in its
        # CDCC adult-care stage (microcosm us_runtime/adult_care.py, added in
        # microcosm PR #638 and aligned to policyengine-us 1.819.0), so on
        # datasets built from that Microcosm surface or later the
        # Section 21(b)(1)(B) dependent route and the Section 21(b)(1)(C)
        # spouse route below fire on measured survey data. Datasets built
        # before that surface leave the flag at its False default, in which
        # case those two routes are inert and the CFTC may be understated for
        # the narrow group of self-care-incapable individuals not already
        # captured by the age or disability conditions. Household-level (web
        # app) calculations honor the user-supplied value and are unaffected.
        incapable = person("is_incapable_of_self_care", period)
        eligible_dependent = dependent & (child | elderly | disabled | incapable)
        count_eligible_dependents = tax_unit.sum(eligible_dependent)
        # A spouse incapable of self-care is a qualifying individual under
        # IRC Section 21(b)(1)(C), incorporated by M.G.L. c. 62
        # Section 6(x)(ii) since 2023. On a joint return there is no legal
        # "primary" taxpayer, so either joint filer who is incapable of
        # self-care is "the spouse of the taxpayer"; we key on
        # is_tax_unit_head_or_spouse rather than is_tax_unit_spouse to avoid
        # a head/spouse ordering (age) artifact. The credit is restricted to
        # joint returns (IRC Section 21(e)(2)), excluding the unmarried
        # sole-filer case.
        # Modeling note: tax unit co-membership proxies the Section 21
        # same-principal-abode test, and the 2024+ noncustodial-parent rule
        # (Section 21 applied without subsection (e)(5)) is not modeled.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        filing_status = tax_unit("ma_filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        self_care_head_or_spouse = head_or_spouse & incapable
        # IRC Section 21(b)(1)(C) recognizes a single "spouse of the
        # taxpayer" qualifying individual, so a joint couple in which both
        # filers are incapable of self-care counts as one qualifying
        # individual, not two.
        has_self_care_spouse = (
            p.disabled_spouse_eligible
            & joint
            & (tax_unit.sum(self_care_head_or_spouse) > 0)
        )
        count_eligible = count_eligible_dependents + has_self_care_spouse
        capped_eligible = min_(count_eligible, p.dependent_cap)
        # Married taxpayers filing separately cannot claim the credit.
        separate = filing_status == filing_status.possible_values.SEPARATE
        return ~separate * capped_eligible * p.amount
