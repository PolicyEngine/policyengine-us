from policyengine_us.model_api import *


class nj_eitc_separate_filer_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets New Jersey's EITC rule for a married separate filer"
    documentation = (
        "N.J.S.A. 54A:4-7a.(3) and N.J.A.C. 18:35-4.3(g)(3) require a married "
        "claimant to file jointly, except one who files as a head of household "
        "or surviving spouse. They have no exception for a separate filer with "
        "a qualifying child who lived apart from the spouse."
    )
    definition_period = YEAR
    reference = (
        # P.L.2021, c.130, section 1a.(3).
        "https://pub.njleg.state.nj.us/Bills/2020/PL21/130_.HTM",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-18-35-4-3",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        person = tax_unit.members
        # IRC 7703(a)(2): a filer separated under a decree is not married.
        under_decree = tax_unit.any(
            person("is_tax_unit_head_or_spouse", period)
            & person("is_separated_under_decree", period)
        )
        return ~separate | under_decree
