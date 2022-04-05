from openfisca_us.model_api import *


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
