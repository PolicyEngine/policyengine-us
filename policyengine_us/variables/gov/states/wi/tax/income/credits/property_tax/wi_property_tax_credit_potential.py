from policyengine_us.model_api import *


class wi_property_tax_credit_potential(Variable):
    """School credit before the ordered nonrefundable-credit limit.

    An unknown head-of-household marital status preserves the legacy potential
    amount for compatibility. wi_property_tax_credit_limit_available is false
    for that case; the ordinary ceiling is not a validated marital-status claim.
    """

    value_type = float
    entity = TaxUnit
    label = "Wisconsin property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=2",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=17",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=17",
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf#page=19",
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=18",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e/c/2",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/9/b",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        rent = add(tax_unit, period, ["rent"])
        ptax = add(tax_unit, period, ["real_estate_taxes"])
        p = parameters(period).gov.states.wi.tax.income.credits.property_tax
        proptax = ptax + rent * p.rent_fraction
        return min_(p.max, proptax * p.rate)

    def formula_2025_01_01(tax_unit, period, parameters):
        rent = add(tax_unit, period, ["rent"])
        ptax = add(tax_unit, period, ["real_estate_taxes"])
        p = parameters(period).gov.states.wi.tax.income.credits.property_tax
        proptax = ptax + rent * p.rent_fraction
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        marital_status = tax_unit(
            "wi_school_property_tax_credit_marital_status", period
        )
        married_head_of_household = (filing_status == statuses.HEAD_OF_HOUSEHOLD) & (
            marital_status == marital_status.possible_values.MARRIED
        )
        separate_ceiling = (
            filing_status == statuses.SEPARATE
        ) | married_head_of_household
        maximum = where(separate_ceiling, p.separate_max, p.max)
        disallowed = tax_unit(
            "wi_veterans_property_tax_credit_incompatible_credits_disallowed",
            period,
        )
        return where(disallowed, 0, min_(proptax * p.rate, maximum))
