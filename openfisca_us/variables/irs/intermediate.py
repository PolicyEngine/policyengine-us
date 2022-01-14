from openfisca_us.model_api import *
from numpy import ceil


class gross_was(Variable):
    value_type = float
    entity = Person
    label = "Gross wage and salary"
    definition_period = YEAR
    unit = USD

    def formula(person, period):
        return add(person, period, "e00200", "pencon")


class txearn_was(Variable):
    value_type = float
    entity = Person
    label = "Taxable gross earnings for OASDI FICA"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        max_earnings = parameters(
            period
        ).irs.payroll.fica.social_security.max_taxable_earnings
        return min_(max_earnings, person("gross_was", period))


class ptax_ss_was(Variable):
    value_type = float
    entity = Person
    label = "OASDI payroll tax on wage income"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        rate = parameters(period).irs.payroll.fica.social_security.rate
        return rate * person("txearn_was", period)


class filer_ptax_ss_was(Variable):
    value_type = float
    entity = TaxUnit
    label = "OASDI payroll tax on wage income for the tax unit (excluding dependents)"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("ptax_ss_was", tax_unit, period)


class ptax_mc_was(Variable):
    value_type = float
    entity = Person
    label = "HI payroll tax on wage income"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        rate = parameters(period).irs.payroll.fica.medicare.rate
        return rate * person("gross_was", period)


class filer_ptax_mc_was(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "HI payroll tax on wage income for the tax unit (excluding dependents)"
    )
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("ptax_mc_was", tax_unit, period)


class sey_frac(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable fraction of self-employment income"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        fica = parameters(period).irs.payroll.fica
        return 1.0 - parameters(period).irs.ald.misc.employer_share * (
            fica.social_security.rate + fica.medicare.rate
        )


class txearn_sey(Variable):
    value_type = float
    entity = Person
    label = "Taxable self-employment income"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        fica = parameters(period).irs.payroll.fica
        ss = fica.social_security
        return min_(
            max_(
                0.0,
                person("sey", period) * person.tax_unit("sey_frac", period),
            ),
            ss.max_taxable_earnings - person("txearn_was", period),
        )


class setax_ss(Variable):
    value_type = float
    entity = Person
    label = "SECA self-employment SS tax"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        rate = parameters(period).irs.payroll.fica.social_security.rate
        return rate * person("txearn_sey", period)


class filer_setax_ss(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "SECA self-employment SS tax for the tax unit (excluding dependents)"
    )
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("setax_ss", tax_unit, period)


class setax_mc(Variable):
    value_type = float
    entity = Person
    label = "SECA self-employment SS tax (Medicare)"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        rate = parameters(period).irs.payroll.fica.medicare.rate
        return rate * max_(
            0, person("sey", period) * person.tax_unit("sey_frac", period)
        )


class setax(Variable):
    value_type = float
    entity = Person
    label = "Self-employment payroll tax"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return add(person, period, "setax_ss", "setax_mc")


class sey_frac_for_extra_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable fraction of self-employment income for extra OASDI payroll taxes"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        fica = parameters(period).irs.payroll.fica
        return (
            1.0
            - parameters(period).irs.ald.misc.employer_share
            * fica.social_security.rate
        )


class extra_payrolltax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Extra payroll tax"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        ss = parameters(period).irs.payroll.fica.social_security
        extra_ss_income = max_(
            0.0,
            tax_unit.members("was_plus_sey", period) - ss.add_taxable_earnings,
        )
        return tax_unit.sum(
            extra_ss_income
            * not_(tax_unit.members("is_tax_unit_dependent", period))
            * ss.rate
        )


class pre_qbid_taxinc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable income (pre-QBID)"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        # Calculate UI excluded from taxable income
        ui = parameters(period).irs.unemployment_insurance
        ui_amount = tax_unit("filer_e02300", period)
        agi_over_ui = tax_unit("c00100", period) - ui_amount
        mars = tax_unit("mars", period)
        return where(
            agi_over_ui <= ui.exemption.cutoff[mars],
            min_(ui_amount, ui.exemption.amount),
            0,
        )


class posagi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Positive AGI"
    unit = USD
    documentation = "Negative AGI values capped at zero"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return max_(tax_unit("c00100", period), 0)


class hasqdivltcg(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Has qualified dividends or long-term capital gains"
    documentation = "Whether this tax unit has qualified dividend income, or long-term capital gains income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Negatives cannot offset other income sources
        INCOME_SOURCES = [
            "c01000",
            "c23650",
            "filer_p23250",
            "filer_e01100",
            "filer_e00650",
        ]
        return np.any(
            [
                tax_unit(income_source, period) > 0
                for income_source in INCOME_SOURCES
            ]
        )


class c33200(Variable):
    value_type = float
    entity = TaxUnit
    label = "Credit for child and dependent care expenses"
    unit = USD
    documentation = "From form 2441, before refundability checks"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).irs.credits.child_and_dep_care
        max_credit = min_(tax_unit("f2441", period), 2) * cdcc.max
        c32800 = max_(0, min_(tax_unit("filer_e32800", period), max_credit))
        mars = tax_unit("mars", period)
        is_head = tax_unit.members("is_tax_unit_head", period)
        earnings = tax_unit.members("earned", period)
        is_spouse = tax_unit.members("is_tax_unit_spouse", period)
        lowest_earnings = where(
            mars == mars.possible_values.JOINT,
            min_(
                tax_unit.sum(is_head * earnings),
                tax_unit.sum(is_spouse * earnings),
            ),
            tax_unit.sum(is_head * earnings),
        )
        c33000 = max_(0, min_(c32800, lowest_earnings))
        c00100 = tax_unit("c00100", period)
        tratio = ceil(
            max_(((c00100 - cdcc.phaseout.start) * cdcc.phaseout.rate), 0)
        )
        exact = tax_unit("exact", period)
        crate = where(
            exact,
            max_(
                cdcc.phaseout.min,
                cdcc.phaseout.max
                - min_(
                    cdcc.phaseout.max - cdcc.phaseout.min,
                    tratio,
                ),
            ),
            max_(
                cdcc.phaseout.min,
                cdcc.phaseout.max
                - max(
                    ((c00100 - cdcc.phaseout.start) * cdcc.phaseout.rate),
                    0,
                ),
            ),
        )
        tratio2 = ceil(
            max_(
                ((c00100 - cdcc.phaseout.second_start) * cdcc.phaseout.rate), 0
            )
        )
        crate_if_over_second_threshold = where(
            exact,
            max_(0, cdcc.phaseout.min - min_(cdcc.phaseout.min, tratio2)),
            max_(
                0,
                cdcc.phaseout.min
                - max_(
                    (
                        (c00100 - cdcc.phaseout.second_start)
                        * cdcc.phaseout.rate
                    ),
                    0,
                ),
            ),
        )
        crate = where(
            c00100 > cdcc.phaseout.second_start,
            crate_if_over_second_threshold,
            crate,
        )

        return c33000 * crate
