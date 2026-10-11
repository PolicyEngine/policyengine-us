from policyengine_us.model_api import *

# Person-level business items that section 461(l) aggregates, in the order
# they are summed: Schedule C, Schedule F, Schedule E rental, Form 4835 farm
# rent, Schedule E estate/trust and partnership/S-corp income. A positive
# amount is business income and a negative amount a business loss.
SECTION_461L_PERSON_ITEMS = [
    "total_self_employment_income",
    "farm_operations_income",
    "rental_income",
    "farm_rent_income",
    "estate_income",
    "partnership_s_corp_income",
]


def section_461l_business_income_and_loss(tax_unit, period):
    """
    The head and spouse's business income and business losses under 461(l).

    Returns the two aggregates section 461(l)(3)(A) compares: gross business
    income and gains, and business deductions, each summed over the items in
    SECTION_461L_PERSON_ITEMS and Form 4797 other net gain. A tax-unit
    dependent's business, rental and estate items belong on the dependent's
    own return, as in irs_gross_income. They neither add to this return's
    losses nor raise its section 461(l) limit.
    """
    person = tax_unit.members
    not_dependent = ~person("is_tax_unit_dependent", period)
    business_income = 0
    business_loss = 0
    for item in SECTION_461L_PERSON_ITEMS:
        amount = person(item, period)
        business_income = business_income + tax_unit.sum(
            not_dependent * max_(0, amount)
        )
        business_loss = business_loss + tax_unit.sum(not_dependent * max_(0, -amount))
    other_net_gain = tax_unit("other_net_gain", period)
    business_income = business_income + max_(0, other_net_gain)
    business_loss = business_loss + max_(0, -other_net_gain)
    return business_income, business_loss


class limited_business_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Business loss deduction allowed under section 461(l)"
    unit = USD
    documentation = (
        "Business, farm, rental, estate and partnership/S corporation losses of "
        "members who are not dependents, deducted above the line up to the "
        "section 461(l) limit: business income plus the threshold amount. "
        "loss_ald is this plus its two capital loss parts."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/165",
        "https://www.law.cornell.edu/uscode/text/26/461#l",
    )

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        # Section 461(l) excess business loss limitation
        threshold_amount = parameters(period).gov.irs.ald.loss.max[filing_status]
        # Section 461(l) compares business deductions to business gross
        # income/gains plus the threshold amount. In this model, positive
        # business amounts flow into gross income and losses are deducted here,
        # so allowable business losses are capped at business income plus
        # the threshold.
        business_income, business_loss = section_461l_business_income_and_loss(
            tax_unit, period
        )
        return min_(business_loss, business_income + threshold_amount)
