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


class invinc_agi_ec(Variable):
    value_type = float
    entity = TaxUnit
    label = "Exclusion of investment income from AGI"
    unit = USD
    documentation = (
        "Always equal to zero (will be removed in a future version)"
    )
    definition_period = YEAR


class invinc_ec_base(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AGI investment income exclusion"
    unit = USD
    documentation = "Exclusion of investment income from AGI"

    def formula(tax_unit, period, parameters):
        # Limitation on net short-term and
        # long-term capital losses
        limited_capital_gain = max_(
            -3000.0 / tax_unit("sep", period),
            add(tax_unit, period, ["filer_p22250", "filer_p23250"]),
        )
        OTHER_INV_INCOME_VARS = ["e00300", "e00600", "e01100", "e01200"]
        other_inv_income = add(
            tax_unit,
            period,
            ["filer_" + variable for variable in OTHER_INV_INCOME_VARS],
        )
        return limited_capital_gain + other_inv_income


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


class c02900(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "'Above the line' AGI deductions"
    unit = USD
    documentation = (
        "Total of all 'above the line' income adjustments to get AGI"
    )

    def formula(tax_unit, period, parameters):
        misc_haircuts = parameters(period).irs.ald.misc.haircut
        BASE_HAIRCUT_VARS = ["c03260", "care_deduction"]
        FILER_HAIRCUT_VARS = [
            "e03210",
            "e03400",
            "e03500",
            "e00800",
            "e03220",
            "e03230",
            "e03240",
            "e03290",
            "e03270",
            "e03150",
            "e03300",
        ]
        haircut_vars = BASE_HAIRCUT_VARS + [
            "filer_" + i for i in FILER_HAIRCUT_VARS
        ]
        return sum(
            [
                (1 - misc_haircuts[variable]) * tax_unit(variable, period)
                for variable in haircut_vars
            ]
        )


class c02500(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable social security benefits"
    documentation = "Social security (OASDI) benefits included in AGI"
    unit = USD

    def formula(tax_unit, period, parameters):
        ss = parameters(period).irs.social_security.taxability
        ymod = tax_unit("ymod", period)
        mars = tax_unit("mars", period)

        lower_threshold = ss.threshold.lower[mars]
        upper_threshold = ss.threshold.upper[mars]

        under_first_threshold = ymod < lower_threshold
        under_second_threshold = ymod < upper_threshold

        e02400 = tax_unit("filer_e02400", period)

        amount_if_under_second_threshold = ss.rate.lower * min_(
            ymod - lower_threshold, e02400
        )
        amount_if_over_second_threshold = min_(
            ss.rate.upper * (ymod - upper_threshold)
            + ss.rate.lower * min_(e02400, upper_threshold - lower_threshold),
            ss.rate.upper * e02400,
        )
        return select(
            [
                under_first_threshold,
                under_second_threshold,
                True,
            ],
            [
                0,
                amount_if_under_second_threshold,
                amount_if_over_second_threshold,
            ],
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
