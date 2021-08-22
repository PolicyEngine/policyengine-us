from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class gross_was_p(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxpayer gross wage and salary"
    definition_period = YEAR

    def formula(tax_unit, period):
        return add(tax_unit, period, "e00200p", "pencon_p")


class gross_was_s(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Spouse gross wage and salary"
    definition_period = YEAR

    def formula(tax_unit, period):
        return add(tax_unit, period, "e00200s", "pencon_s")


class txearn_was_p(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxpayer taxable gross earnings for OASDI FICA"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        max_earnings = parameters(
            period
        ).tax.payroll.FICA.social_security.max_taxable_earnings
        return min_(max_earnings, tax_unit("gross_was_p", period))


class txearn_was_s(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Spouse taxable gross earnings for OASDI FICA"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        max_earnings = parameters(
            period
        ).tax.payroll.FICA.social_security.max_taxable_earnings
        return min_(max_earnings, tax_unit("gross_was_s", period))


class ptax_ss_was_p(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxpayer OASDI payroll tax on wage income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        rate = parameters(period).tax.payroll.FICA.social_security.tax_rate
        return rate * tax_unit("txearn_was_p", period)


class ptax_ss_was_s(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Spouse OASDI payroll tax on wage income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        rate = parameters(period).tax.payroll.FICA.social_security.tax_rate
        return rate * tax_unit("txearn_was_s", period)


class ptax_mc_was_p(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxpayer HI payroll tax on wage income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        rate = parameters(period).tax.payroll.FICA.medicare.tax_rate
        return rate * tax_unit("gross_was_p", period)


class ptax_mc_was_s(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Spouse HI payroll tax on wage income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        rate = parameters(period).tax.payroll.FICA.social_security.tax_rate
        return rate * tax_unit("gross_was_s", period)


class sey_frac(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxable fraction of self-employment income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        FICA = parameters(period).tax.payroll.FICA
        sey_frac = 1.0 - 0.5 * (
            FICA.social_security.tax_rate + FICA.medicare.tax_rate
        )
        return sey_frac


class txearn_sey_p(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxpayer taxable self-employment income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        FICA = parameters(period).tax.payroll.FICA
        SS = FICA.social_security
        MC = FICA.medicare
        txearn_sey_p = min_(
            max_(
                0.0, tax_unit("sey_p", period) * tax_unit("sey_frac", period)
            ),
            SS.max_taxable_earnings - tax_unit("txearn_was_p", period),
        )
        return txearn_sey_p


class txearn_sey_s(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Spouse taxable self-employment income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        FICA = parameters(period).tax.payroll.FICA
        SS = FICA.social_security
        MC = FICA.medicare
        txearn_sey_p = min_(
            max_(
                0.0, tax_unit("sey_s", period) * tax_unit("sey_frac", period)
            ),
            SS.max_taxable_earnings - tax_unit("txearn_was_s", period),
        )
        return txearn_sey_p


class setax_ss_p(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxpayer SECA self-employment SS tax"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        rate = parameters(period).tax.payroll.FICA.social_security.tax_rate
        return rate * tax_unit("txearn_sey_p", period)


class setax_ss_s(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Spouse SECA self-employment SS tax"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        rate = parameters(period).tax.payroll.FICA.social_security.tax_rate
        return rate * tax_unit("txearn_sey_s", period)


class setax_mc_p(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxpayer SECA self-employment SS tax (Medicare)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        rate = parameters(period).tax.payroll.FICA.medicare.tax_rate
        return rate * max_(
            0, tax_unit("sey_p", period) * tax_unit("sey_frac", period)
        )


class setax_mc_s(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Spouse SECA self-employment SS tax (Medicare)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        rate = parameters(period).tax.payroll.FICA.medicare.tax_rate
        return rate * max_(
            0, tax_unit("sey_s", period) * tax_unit("sey_frac", period)
        )


class setax_p(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxpayer self-employment payroll tax"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, "setax_ss_p", "setax_mc_p")


class setax_s(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Spouse self-employment payroll tax"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, "setax_ss_s", "setax_mc_s")


class sey_frac_for_extra_OASDI(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxable fraction of self-employment income for extra OASDI payroll taxes"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        FICA = parameters(period).tax.payroll.FICA
        sey_frac = 1.0 - 0.5 * FICA.social_security.tax_rate
        return sey_frac


class extra_payrolltax(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Extra payroll tax"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        SS = parameters(period).tax.payroll.FICA.social_security
        extra_ss_income_p = max(
            0.0, tax_unit("was_plus_sey_p", period) - SS.add_taxable_earnings
        )
        extra_ss_income_s = max(
            0.0, tax_unit("was_plus_sey_s", period) - SS.add_taxable_earnings
        )
        return (
            extra_ss_income_p * SS.tax_rate + extra_ss_income_s * SS.tax_rate
        )
