from policyengine_us.model_api import *


class az_family_tax_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Family Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.azleg.gov/ars/43/01073.htm",
        "https://www.azleg.gov/ars/43/01001.htm",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = "az_family_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.family_tax_credits.amount
        filing_status = tax_unit("filing_status", period)
        # A.R.S. 43-1073(B): $40 "for each person ... who is either the
        # taxpayer, the taxpayer's spouse who does not file a return or a
        # dependent". A filer whom another taxpayer can claim still counts as
        # the taxpayer, but "dependent" has the IRC 152 meaning (A.R.S.
        # 43-1001(3)), so under IRC 152(b)(1) a return on which the filer (or,
        # if joint, either spouse) can be claimed counts no dependents.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        disallowed_dependents = where(
            filer_is_dependent, tax_unit("tax_unit_dependents", period), 0
        )
        persons = tax_unit("tax_unit_size", period) - disallowed_dependents
        amount = p.per_person * persons
        return min_(amount, p.cap[filing_status])
