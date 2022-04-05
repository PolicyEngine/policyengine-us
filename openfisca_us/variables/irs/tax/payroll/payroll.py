from openfisca_us.model_api import *


class payrolltax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Payroll tax"
    definition_period = YEAR
    unit = USD
    documentation = "Total (employee + employer) payroll tax liability."

    def formula(tax_unit, period):
        COMPONENTS = [
            "ptax_was",
            "ptax_amc",
            "filer_setax",
        ]
        return add(tax_unit, period, COMPONENTS)


class employee_payrolltax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Employee's payroll tax"
    documentation = "Share of payroll tax liability paid by the employee."
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit("payrolltax", period) * 0.5


class ptax_amc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Additional Medicare Tax"
    unit = USD
    documentation = (
        "Additional Medicare Tax from Form 8959 (included in payrolltax)"
    )

    def formula(tax_unit, period, parameters):
        payroll = parameters(period).irs.payroll
        positive_sey = max_(0, tax_unit("filer_sey", period))
        combined_rate = (
            payroll.medicare.employee.main.rate
            + payroll.social_security.employee.rate
        )
        line8 = positive_sey * (1 - combined_rate)
        mars = tax_unit("mars", period)
        e00200 = tax_unit("filer_e00200", period)
        exclusion = payroll.medicare.additional.exclusion[mars]
        earnings_over_exclusion = max_(0, e00200 - exclusion)
        line11 = max_(0, exclusion - e00200)
        rate = payroll.medicare.additional.rate
        base = earnings_over_exclusion + max_(0, line8 - line11)
        return rate * base


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


class sey_frac(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable fraction of self-employment income"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        irs = parameters(period).irs
        ss = irs.payroll.fica.social_security
        ss_combined_rate = ss.employee.rate + ss.employer.rate
        mc = irs.payroll.fica.medicare
        mc_combined_rate = mc.employee.main.rate + mc.employer.rate
        combined_fica_rate = ss_combined_rate + mc_combined_rate
        return 1.0 - irs.ald.misc.employer_share * combined_fica_rate


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


class setax_mc(Variable):
    value_type = float
    entity = Person
    label = "SECA self-employment SS tax (Medicare)"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        se = parameters(period).irs.payroll.medicare.self_employment
        base = max_(
            0, person("sey", period) * person.tax_unit("sey_frac", period)
        )
        return se.main.rate * base


class setax(Variable):
    value_type = float
    entity = Person
    label = "Self-employment payroll tax"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return add(person, period, ["setax_ss", "setax_mc"])


class sey_frac_for_extra_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable fraction of self-employment income for extra OASDI payroll taxes"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        irs = parameters(period).irs
        rate = irs.payroll.social_security.self_employment.rate
        return 1.0 - irs.ald.misc.employer_share * rate
