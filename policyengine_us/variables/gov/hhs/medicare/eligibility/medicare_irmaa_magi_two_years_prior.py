from policyengine_us.model_api import *
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR

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


class medicare_irmaa_magi_two_years_prior(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicare IRMAA MAGI from two years prior"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395r#i_4",
        "https://www.law.cornell.edu/uscode/text/26/135#c_1",
        "https://www.irs.gov/pub/irs-prior/f8815--2025.pdf#page=3",
    )
    documentation = (
        "Modified adjusted gross income used to determine Medicare IRMAA "
        "charges. Callers may provide this value directly for the current "
        "benefit year. When it is not provided, PolicyEngine computes it from "
        "two years prior as adjusted gross income plus the head's and "
        "spouse's tax-exempt interest and the amounts excluded or deducted "
        "under IRC sections 135, 911, 931 and 933. "
        "Single-year datasets without lagged income inputs therefore default "
        "to the modeled prior-year values, which may be zero. When the year "
        "two years prior precedes the first year PolicyEngine models (2015), "
        "only income provided for that year counts, and the rest is zero."
    )

    def formula(tax_unit, period, parameters):
        prior_period = period.offset(-2, "year")
        if prior_period.start.year >= FIRST_MODELED_YEAR:
            filer_amounts = parameters(
                prior_period
            ).gov.irs.ald.filer_amounts_recorded_on_dependents
            return add(
                tax_unit,
                prior_period,
                ["adjusted_gross_income", *TAX_UNIT_ADDITIONS],
            ) + tax_unit_non_dep_add(
                tax_unit,
                prior_period,
                PERSON_ADDITIONS,
                include_dependents=filer_amounts,
            )
        # Benefit years 2015 and 2016 look back to 2013 and 2014, before the
        # parameters begin, so income for those years cannot be computed. Use
        # income provided for them and treat the rest as zero, the value the
        # formula yields in later years when no prior-year income is provided.
        # Reading stored values computes and caches nothing for those years;
        # tax unit roles are the benefit year's.
        simulation = tax_unit.simulation
        filer_amounts = parameters(
            period
        ).gov.irs.ald.filer_amounts_recorded_on_dependents
        dependent = tax_unit.members("is_tax_unit_dependent", period)

        def provided(variable, population):
            holder = simulation.get_holder(variable)
            value = holder.get_array(prior_period, simulation.branch_name)
            if value is None and variable == "section_911_excluded_income":
                # Defaults to the stacking amount, as its formula does.
                return provided("foreign_earned_income_exclusion", population)
            return population.empty_array() if value is None else value

        magi = provided("adjusted_gross_income", tax_unit)
        for variable in TAX_UNIT_ADDITIONS:
            magi = magi + provided(variable, tax_unit)
        for variable in PERSON_ADDITIONS:
            amount = provided(variable, tax_unit.members)
            if variable not in filer_amounts:
                amount = where(dependent, 0, amount)
            magi = magi + tax_unit.sum(amount)
        return magi
