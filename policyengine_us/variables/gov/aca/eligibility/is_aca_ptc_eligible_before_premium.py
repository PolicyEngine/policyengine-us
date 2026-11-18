from policyengine_us.model_api import *


class is_aca_ptc_eligible_before_premium(Variable):
    value_type = bool
    entity = Person
    label = "Person meets ACA premium tax credit conditions before premium payment"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-2#b",
    )
    documentation = (
        "The tax-family, filing-status and income conditions for premium tax "
        "credit eligibility, before the enrollment and premium-payment "
        "conditions. An enrolled fourth child can meet these conditions "
        "even though the three-child rating limit means no marginal premium "
        "is charged. These conditions therefore apply to every enrollee "
        "when determining shared-policy cost-sharing reductions."
    )

    def formula(person, period, parameters):
        fstatus = person.tax_unit("filing_status", period)
        separate = fstatus == fstatus.possible_values.SEPARATE

        p = parameters(period).gov.aca
        magi_frac = person.tax_unit("aca_magi_fraction", period)
        standard_income_eligible = p.ptc_income_eligibility.calc(magi_frac)
        below_fpl_exception = person.tax_unit(
            "aca_ptc_below_fpl_immigration_exception", period
        )
        is_income_eligible = standard_income_eligible | below_fpl_exception

        # Someone another taxpayer can claim is not an applicable taxpayer
        # (IRC 36B(c)(1)(D), 26 CFR 1.36B-2(b)(3)). The family variable also
        # applies the dependent-taxpayer rule in IRC 152(b)(1).
        tax_family_member = person("is_aca_tax_family_member", period)
        return tax_family_member & ~separate & is_income_eligible
