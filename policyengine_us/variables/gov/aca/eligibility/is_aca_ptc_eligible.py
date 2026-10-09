from policyengine_us.model_api import *


class is_aca_ptc_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for ACA premium tax credit and pays ACA premium"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-2#b",
    )

    def formula(person, period, parameters):
        fstatus = person.tax_unit("filing_status", period)
        separate = fstatus == fstatus.possible_values.SEPARATE

        # determine income eligibility for ACA PTC
        p = parameters(period).gov.aca
        magi_frac = person.tax_unit("aca_magi_fraction", period)
        standard_income_eligible = p.ptc_income_eligibility.calc(magi_frac)
        below_fpl_exception = person.tax_unit(
            "aca_ptc_below_fpl_immigration_exception", period
        )
        is_income_eligible = standard_income_eligible | below_fpl_exception

        # Someone another taxpayer can claim is not an applicable taxpayer
        # (26 U.S.C. 36B(c)(1)(D)) and is outside the tax family, along with
        # the dependents of a return that has such a filer.
        tax_family_member = person("is_aca_tax_family_member", period)

        return (
            person("pays_aca_premium", period)
            & tax_family_member
            & ~separate
            & is_income_eligible
        )
