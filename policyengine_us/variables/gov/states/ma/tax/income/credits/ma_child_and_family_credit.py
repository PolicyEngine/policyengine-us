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
        # A disabled spouse is a qualifying individual under
        # IRC Section 21(b)(1)(C), incorporated by M.G.L. c. 62
        # Section 6(x)(1)(ii) since 2023.
        spouse = person("is_tax_unit_spouse", period)
        eligible_spouse = p.disabled_spouse_eligible & spouse & disabled
        eligible = eligible_dependent | eligible_spouse
        count_eligible = tax_unit.sum(eligible)
        capped_eligible = min_(count_eligible, p.dependent_cap)
        # Married taxpayers filing separately cannot claim the credit.
        filing_status = tax_unit("ma_filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return ~separate * capped_eligible * p.amount
