from openfisca_us.model_api import *


class posagi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Positive AGI"
    unit = USD
    documentation = "Negative AGI values capped at zero"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return max_(tax_unit("c00100", period), 0)


class ymod(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "OASDI benefit tax variable"
    documentation = "Variable that is used in OASDI benefit taxation logic"
    unit = USD

    def formula(tax_unit, period, parameters):
        ymod2 = (
            tax_unit("filer_e00400", period)
            + (0.5 * tax_unit("filer_e02400", period))
            - tax_unit("c02900", period)
        )
        YMOD3_ELEMENTS = ["filer_e03210", "filer_e03230", "filer_e03240"]
        ymod3 = add(tax_unit, period, YMOD3_ELEMENTS)
        return tax_unit("ymod1", period) + ymod2 + ymod3


class ymod1(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AGI increase"
    documentation = "Variable that is included in AGI"
    unit = USD

    def formula(tax_unit, period, parameters):
        DIRECT_INPUTS = [
            "e00200",
            "e00700",
            "e00800",
            "e01400",
            "e01700",
            "e02100",
            "e02300",
        ]
        direct_inputs = add(
            tax_unit,
            period,
            ["filer_" + variable for variable in DIRECT_INPUTS],
        )
        INVESTMENT_INCOME_SOURCES = [
            "e00300",
            "e00600",
            "e01100",
            "e01200",
        ]
        investment_income_sources = [
            "filer_" + variable for variable in INVESTMENT_INCOME_SOURCES
        ]
        investment_income = add(
            tax_unit, period, investment_income_sources
        ) + tax_unit("c01000", period)
        BUSINESS_INCOME_SOURCES = ["filer_e00900", "filer_e02000"]
        business_income = add(tax_unit, period, BUSINESS_INCOME_SOURCES)
        max_business_losses = parameters(
            period
        ).irs.ald.misc.max_business_losses[tax_unit("mars", period)]
        business_income_losses_capped = max_(
            business_income, -max_business_losses
        )
        return (
            direct_inputs + investment_income + business_income_losses_capped
        )


class c00100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AGI"
    documentation = "Adjusted Gross Income"
    unit = USD

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["ymod1", "c02500", "c02900"])


adjusted_gross_income = variable_alias("adjusted_gross_income", c00100)
