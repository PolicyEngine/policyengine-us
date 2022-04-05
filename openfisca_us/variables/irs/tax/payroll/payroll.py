from openfisca_us.model_api import *


class ptax_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Employee + employer OASDI FICA tax plus self-employment tax (excludes HI FICA so positive ptax_oasdi is less than ptax_was plus setax)"
    unit = USD

    def formula(tax_unit, period):
        ELEMENTS = ["filer_ptax_ss_was", "filer_setax_ss"]
        return add(tax_unit, period, ELEMENTS)


class ptax_was(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Employee-side OASDI + HI FICA tax"
    unit = USD

    def formula(tax_unit, period, parameters):
        ELEMENTS = ["filer_ptax_ss_was", "filer_ptax_mc_was"]
        return add(tax_unit, period, ELEMENTS)


class ptax_mc_was(Variable):
    value_type = float
    entity = Person
    label = "Employee-side health insurance payroll tax on wage income"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        rate = parameters(period).irs.payroll.fica.medicare.employee.main.rate
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


class txearn_sey(Variable):
    value_type = float
    entity = Person
    label = "Taxable self-employment income"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        ss = parameters(period).irs.payroll.fica.social_security
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
        se = parameters(period).irs.payroll.social_security.self_employment
        return se.rate * person("txearn_sey", period)


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
