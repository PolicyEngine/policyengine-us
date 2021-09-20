from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class gross_was(Variable):
    value_type = float
    entity = Person
    label = u"Gross wage and salary"
    definition_period = YEAR

    def formula(person, period):
        return add(person, period, "e00200", "pencon")


class txearn_was(Variable):
    value_type = float
    entity = Person
    label = u"Taxable gross earnings for OASDI FICA"
    definition_period = YEAR

    def formula(person, period, parameters):
        max_earnings = parameters(
            period
        ).tax.payroll.FICA.social_security.max_taxable_earnings
        return min_(max_earnings, person("gross_was", period))


class ptax_ss_was(Variable):
    value_type = float
    entity = Person
    label = u"OASDI payroll tax on wage income"
    definition_period = YEAR

    def formula(person, period, parameters):
        rate = parameters(period).tax.payroll.FICA.social_security.tax_rate
        return rate * person("txearn_was", period)


class filer_ptax_ss_was(Variable):
    value_type = float
    entity = TaxUnit
    label = u"OASDI payroll tax on wage income for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("ptax_ss_was", tax_unit, period)


class ptax_mc_was(Variable):
    value_type = float
    entity = Person
    label = u"HI payroll tax on wage income"
    definition_period = YEAR

    def formula(person, period, parameters):
        rate = parameters(period).tax.payroll.FICA.medicare.tax_rate
        return rate * person("gross_was", period)


class filer_ptax_mc_was(Variable):
    value_type = float
    entity = TaxUnit
    label = u"HI payroll tax on wage income for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("ptax_mc_was", tax_unit, period)


class sey_frac(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxable fraction of self-employment income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        FICA = parameters(period).tax.payroll.FICA
        return 1.0 - parameters(period).tax.ALD.misc.employer_share * (
            FICA.social_security.tax_rate + FICA.medicare.tax_rate
        )


class txearn_sey(Variable):
    value_type = float
    entity = Person
    label = u"Taxable self-employment income"
    definition_period = YEAR

    def formula(person, period, parameters):
        FICA = parameters(period).tax.payroll.FICA
        SS = FICA.social_security
        MC = FICA.medicare
        return min_(
            max_(
                0.0,
                person("sey", period) * person.tax_unit("sey_frac", period),
            ),
            SS.max_taxable_earnings - person("txearn_was", period),
        )


class setax_ss(Variable):
    value_type = float
    entity = Person
    label = u"SECA self-employment SS tax"
    definition_period = YEAR

    def formula(person, period, parameters):
        rate = parameters(period).tax.payroll.FICA.social_security.tax_rate
        return rate * person("txearn_sey", period)


class filer_setax_ss(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        u"SECA self-employment SS tax for the tax unit (excluding dependents)"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("setax_ss", tax_unit, period)


class setax_mc(Variable):
    value_type = float
    entity = Person
    label = u"SECA self-employment SS tax (Medicare)"
    definition_period = YEAR

    def formula(person, period, parameters):
        rate = parameters(period).tax.payroll.FICA.medicare.tax_rate
        return rate * max_(
            0, person("sey", period) * person.tax_unit("sey_frac", period)
        )


class setax(Variable):
    value_type = float
    entity = Person
    label = u"Self-employment payroll tax"
    definition_period = YEAR

    def formula(person, period, parameters):
        return add(person, period, "setax_ss", "setax_mc")


class sey_frac_for_extra_OASDI(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxable fraction of self-employment income for extra OASDI payroll taxes"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        FICA = parameters(period).tax.payroll.FICA
        return (
            1.0
            - parameters(period).tax.ALD.misc.employer_share
            * FICA.social_security.tax_rate
        )


class extra_payrolltax(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Extra payroll tax"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        SS = parameters(period).tax.payroll.FICA.social_security
        extra_ss_income = max_(
            0.0,
            tax_unit.members("was_plus_sey", period) - SS.add_taxable_earnings,
        )
        return tax_unit.sum(
            extra_ss_income
            * not_(tax_unit.members("is_tax_unit_dependent", period))
            * SS.tax_rate
        )


class pre_qbid_taxinc(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxable income (pre-QBID)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Calculate UI excluded from taxable income
        MARS = tax_unit("MARS", period)
        UI = parameters(period).benefit.unemployment_insurance
        UI_amount = tax_unit("filer_e02300", period)
        AGI_over_UI = tax_unit("c00100", period) - UI_amount
        return where(
            AGI_over_UI <= UI.exemption.cutoff,
            min_(UI_amount, UI.exemption.amount),
            0,
        )
