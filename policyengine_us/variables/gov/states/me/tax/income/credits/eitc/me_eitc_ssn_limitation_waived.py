from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import eitc_filing_requirement_met


class me_eitc_ssn_limitation_waived(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maine waives the EITC's Social Security number limitation"
    documentation = "Whether Maine computes its earned income tax credit without the IRC 32(m) Social Security number limitation. From 2021 it does for a return whose filer files a federal income tax return (36 M.R.S. § 5219-S(7)): one required to file, filing voluntarily, or that would file to claim a refundable credit, Maine's own included."
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5219-S.html",
        "https://www.law.cornell.edu/uscode/text/26/32#m",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.eitc
        # § 5219-S(7) applies "for an individual who files a federal income
        # tax return". This reads filing as the federal eitc formula does:
        # required to file, filing voluntarily, or would file to claim a
        # refundable credit. Maine's EITC is refundable and, for an ITIN
        # filer, needs that federal return, so a filer who would file for a
        # credit files for it. tax_unit_is_filer counts only federal credits
        # (eligible_for_refundable_credits), which 32(m) denies this filer,
        # so it calls such a filer a nonfiler where an SSN twin with the same
        # inputs and a federal credit files. The condition is read on the
        # return as filed: the childless pro forma sets voluntary filing only
        # inside its own branch.
        return p.itin_eligible & eitc_filing_requirement_met(tax_unit, period)
