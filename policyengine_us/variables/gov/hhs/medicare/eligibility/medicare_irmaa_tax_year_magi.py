from policyengine_us.model_api import *

# 42 U.S.C. 1395r(i)(4)(A): adjusted gross income (i) determined without
# regard to sections 135, 911, 931 and 933 of the Internal Revenue Code and
# (ii) increased by tax-exempt interest. Income inputs are net of the section
# 911 amounts (Form 2555 lines 45 and 50); sections 135, 931 and 933 are
# above-the-line deductions in this model. Adding each amount back undoes it.
TAX_UNIT_ADDITIONS = [
    "section_911_excluded_income",
    "specified_possession_income",
    "puerto_rico_income",
]
# Person-level amounts on the filer's return, summed over the members whose
# amounts adjusted gross income counts: the head and spouse, and every member
# for amounts listed in gov.irs.ald.filer_amounts_recorded_on_dependents. A
# dependent's own tax-exempt interest is on the dependent's return. The
# section 135 exclusion is listed: only a bond issued to an owner aged 24 or
# older qualifies (26 U.S.C. 135(c)(1)(B); Form 8815), so an amount recorded
# on a dependent is the filer's exclusion for the dependent's tuition, which
# adjusted gross income deducts and this adds back.
PERSON_ADDITIONS = ["tax_exempt_interest_income", "us_bonds_for_higher_ed"]


class medicare_irmaa_tax_year_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicare IRMAA MAGI on this tax year's return"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395r#i_4",
        "https://www.law.cornell.edu/uscode/text/26/135#c_1",
        "https://www.irs.gov/pub/irs-prior/f8815--2025.pdf#page=3",
    )
    documentation = (
        "Modified adjusted gross income as Medicare IRMAA defines it, from "
        "this tax year's income: adjusted gross income plus the head's and "
        "spouse's tax-exempt interest and the amounts excluded or deducted "
        "under IRC sections 135, 911, 931 and 933. IRMAA for a benefit year "
        "normally applies this amount from two years earlier "
        "(medicare_irmaa_magi_two_years_prior)."
    )

    def formula(tax_unit, period, parameters):
        filer_amounts = parameters(
            period
        ).gov.irs.ald.filer_amounts_recorded_on_dependents
        return add(
            tax_unit,
            period,
            ["adjusted_gross_income", *TAX_UNIT_ADDITIONS],
        ) + tax_unit_non_dep_add(
            tax_unit,
            period,
            PERSON_ADDITIONS,
            include_dependents=filer_amounts,
        )
