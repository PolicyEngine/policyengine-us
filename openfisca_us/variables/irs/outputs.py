from openfisca_us.model_api import *
from numpy import ceil


class sey(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return add(person, period, ["e00900", "e02100", "k1bx14"])


class filer_sey(Variable):
    value_type = float
    entity = TaxUnit
    label = "sey for the tax unit (excluding dependents)"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("sey", tax_unit, period)


class combined(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxes"
    documentation = "Total federal income and payroll tax liability."
    unit = USD

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["iitax", "employee_payrolltax"])


tax = variable_alias("tax", combined)


class filer_earned(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("earned", tax_unit, period)


class earned(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Earned income"
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD

    def formula(person, period, parameters):
        ald = parameters(period).irs.ald
        adjustment = (
            (1.0 - ald.misc.self_emp_tax_adj)
            * ald.misc.employer_share
            * person("setax", period)
        )
        return max_(0, add(person, period, ["e00200", "setax"]) - adjustment)


earned_income = variable_alias("earned_income", earned)


class was_plus_sey(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD

    def formula(person, period, parameters):
        return person("gross_was", period) + max_(
            0,
            person("sey", period)
            * person.tax_unit("sey_frac_for_extra_oasdi", period),
        )


class exact(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )


class expanded_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Expanded income"
    documentation = "Broad income measure that includes benefit_value_total"
    unit = USD

    def formula(tax_unit, period, parameters):
        FILER_COMPONENTS = [
            "e00200",
            "pencon",
            "e00300",
            "e00400",
            "e00600",
            "e00700",
            "e00800",
            "e00900",
            "e01100",
            "e01200",
            "e01400",
            "e01500",
            "e02000",
            "e02100",
            "p22250",
            "p23250",
            "cmbtp",
        ]
        filer_components = add(
            tax_unit,
            period,
            [f"filer_{component}" for component in FILER_COMPONENTS],
        )
        return (
            filer_components
            + 0.5 * tax_unit("ptax_was", period)
            + tax_unit("benefit_value_total", period)
        )


class othertaxes(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Other taxes: sum of niit, e09700, e09800 and e09900 (included in c09200)"
    unit = USD


class sep(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    default_value = 1
    documentation = "2 when MARS is 3 (married filing separately); otherwise 1"


class filer_sey(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "sey for the tax unit (excluding dependents)"
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("sey", tax_unit, period)


class surtax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


class c01000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Limitation on capital losses"
    unit = USD

    def formula(tax_unit, period, parameters):
        return max_(
            (-3000.0 / tax_unit("sep", period)), tax_unit("c23650", period)
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


class c03260(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        ald = parameters(period).irs.ald
        return (
            (1.0 - ald.misc.self_emp_tax_adj)
            * ald.misc.employer_share
            * tax_unit.sum(tax_unit.members("setax", period))
        )


class c04470(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Itemized deductions after phase-out"
    unit = USD
    documentation = (
        "Itemized deductions after phase-out (zero for non-itemizers)"
    )

    def formula(tax_unit, period, parameters):
        return max_(0, tax_unit("c21060", period) - tax_unit("c21040", period))


class c05700(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


class c05800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax before credits"
    unit = USD
    documentation = "Total (regular + AMT) income tax liability before credits (equals taxbc plus c09600)"

    def formula(tax_unit, period, parameters):
        return add(
            tax_unit,
            period,
            ["regular_tax_before_credits", "alternative_minimum_tax"],
        )


income_tax_before_credits = variable_alias("income_tax_before_credits", c05800)


class c07100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax non-refundable credits"
    documentation = (
        "Total non-refundable credits used to reduce positive tax liability"
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        credits = parameters(period).irs.credits.non_refundable
        return add(tax_unit, period, credits)


income_tax_non_refundable_credits = variable_alias(
    "income_tax_non_refundable_credits", c07100
)


class c07240(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


class c07260(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


class c07300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


class c07400(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


class c07600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


class c08000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


class c09200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Income tax before refundable credits"
    documentation = "Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied"

    def formula(tax_unit, period, parameters):
        return max_(
            0,
            tax_unit("income_tax_before_credits", period)
            - tax_unit("income_tax_non_refundable_credits", period),
        )


income_tax_before_refundable_credits = variable_alias(
    "income_tax_before_refundable_credits", c09200
)


class c17000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Medical expense deduction"
    unit = USD
    documentation = "Sch A: Medical expenses deducted (component of pre-limitation c21060 total)"

    def formula(tax_unit, period, parameters):
        medical = parameters(period).irs.deductions.itemized.medical
        has_aged = (tax_unit("age_head", period) >= 65) | (
            tax_unit("tax_unit_is_joint", period)
            & (tax_unit("age_spouse", period) >= 65)
        )
        medical_floor_ratio = (
            medical.floor.base + has_aged * medical.floor.aged_addition
        )
        medical_floor = medical_floor_ratio * max_(
            tax_unit("c00100", period), 0
        )
        return max_(
            0,
            tax_unit("filer_e17500", period) - medical_floor,
        )


class c18300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "SALT deduction"
    unit = USD
    documentation = "Sch A: State and local taxes plus real estate taxes deducted (component of pre-limitation c21060 total)"

    def formula(tax_unit, period, parameters):
        c18400 = max_(tax_unit("filer_e18400", period), 0)
        c18500 = tax_unit("filer_e18500", period)
        salt = parameters(period).irs.deductions.itemized.salt_and_real_estate
        cap = salt.cap[tax_unit("mars", period)]
        return min_(c18400 + c18500, cap)


class c19200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Interest deduction"
    unit = USD
    documentation = (
        "Sch A: Interest deducted (component of pre-limitation c21060 total)"
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("filer_e19200", period)


class c19700(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Charitable deduction"
    unit = USD
    documentation = "Sch A: Charity contributions deducted (component of pre-limitation c21060 total)"

    def formula(tax_unit, period, parameters):
        charity = parameters(period).irs.deductions.itemized.charity
        posagi = tax_unit("posagi", period)
        lim30 = min_(
            charity.ceiling.non_cash * posagi,
            tax_unit("filer_e20100", period),
        )
        c19700 = min_(
            charity.ceiling.all * posagi,
            lim30 + tax_unit("filer_e19800", period),
        )
        return max_(c19700, 0)


class c20500(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Casualty deduction"
    unit = USD
    documentation = "Sch A: Net casualty or theft loss deducted (component of pre-limitation c21060 total)"

    def formula(tax_unit, period, parameters):
        casualty = parameters(period).irs.deductions.itemized.casualty
        floor = casualty.floor * tax_unit("posagi", period)
        deduction = max_(0, tax_unit("filer_g20500", period) - floor)
        return deduction * (1 - casualty.haircut)


class c20800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Miscellaneous deductions"
    unit = USD
    documentation = "Sch A: Net limited miscellaneous deductions deducted (component of pre-limitation c21060 total)"

    def formula(tax_unit, period, parameters):
        misc = parameters(period).irs.deductions.itemized.misc
        floor = misc.floor * tax_unit("posagi", period)
        deduction = max_(0, tax_unit("filer_e20400", period) - floor)
        return deduction * (1 - misc.haircut)


class c21040(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Phased-out itemized deductions"
    unit = USD
    documentation = "Itemized deductions that are phased out"

    def formula(tax_unit, period, parameters):
        nonlimited = add(tax_unit, period, ["c17000", "c20500"])
        phaseout = parameters(period).irs.deductions.itemized.phaseout
        mars = tax_unit("mars", period)
        c21060 = tax_unit("c21060", period)
        phaseout_amount_cap = phaseout.cap * max_(0, c21060 - nonlimited)
        uncapped_phaseout = max_(
            0,
            (
                (tax_unit("posagi", period) - phaseout.start[mars])
                * phaseout.rate
            ),
        )
        return min_(
            uncapped_phaseout,
            phaseout_amount_cap,
        )


class c21060(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Gross itemized deductions"
    unit = USD
    documentation = (
        "Itemized deductions before phase-out (zero for non-itemizers)"
    )

    def formula(tax_unit, period, parameters):
        ELEMENTS = ["c17000", "c18300", "c19200", "c19700", "c20500", "c20800"]
        return add(tax_unit, period, ELEMENTS)


class c23650(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Net capital gains"
    unit = USD
    documentation = "Net capital gains (long and short term) before exclusion"

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["filer_p23250", "filer_p22250"])


class tax_unit_is_joint(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Joint-filing tax unit"
    documentation = "Whether this tax unit is a joint filer."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        mars = tax_unit("mars", period)
        return mars == mars.possible_values.JOINT


class c62100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) taxable income"

    def formula(tax_unit, period, parameters):
        # Form 6251, Part I
        c00100 = tax_unit("c00100", period)
        e00700 = tax_unit("filer_e00700", period)
        c62100_if_no_standard = (
            c00100
            - e00700
            - tax_unit("c04470", period)
            + max_(
                0,
                min_(
                    tax_unit("c17000", period),
                    0.025 * c00100,
                ),
            )
            + tax_unit("c18300", period)
            + tax_unit("c20800", period)
            - tax_unit("c21040", period)
        )
        c62100 = where(
            tax_unit("standard", period) == 0,
            c62100_if_no_standard,
            c00100 - e00700,
        ) + tax_unit(
            "filer_cmbtp", period
        )  # add income not in AGI but considered income for AMT
        amt = parameters(period).irs.income.amt
        mars = tax_unit("mars", period)
        separate_addition = max_(
            0,
            min_(
                amt.exemption.amount[mars],
                amt.exemption.phaseout.rate
                * (c62100 - amt.exemption.separate_limit),
            ),
        ) * (mars == mars.possible_values.SEPARATE)
        return c62100 + separate_addition


class c87668(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    documentation = "American Opportunity Credit non-refundable amount from Form 8863 (included in c07230)"

    def formula(tax_unit, period, parameters):
        return tax_unit("non_refundable_american_opportunity_credit", period)


class care_deduction(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )


class ctc_new(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


class recovery_rebate_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Recovery Rebate Credit"
    documentation = (
        "Recovery Rebate Credit, from American Rescue Plan Act of 2021"
    )
    unit = USD


class charity_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Credit for charitable giving"
    unit = USD


class dwks6(Variable):
    value_type = float
    entity = TaxUnit
    label = "DWKS6"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        dwks2 = tax_unit("filer_e00650", period)
        dwks3 = tax_unit("filer_e58990", period)
        # dwks4 always assumed to be zero
        dwks5 = max_(0, dwks3)
        return max_(0, dwks2 - dwks5)


class dwks9(Variable):
    value_type = float
    entity = TaxUnit
    label = "DWKS9"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p23250 = tax_unit("filer_p23250", period)
        c23650 = tax_unit("c23650", period)
        dwks7 = min_(p23250, c23650)  # SchD lines 15 and 16, respectively
        # dwks8 = min(dwks3, dwks4)
        # dwks9 = max(0., dwks7 - dwks8)
        # BELOW TWO STATEMENTS ARE UNCLEAR IN LIGHT OF dwks9=... COMMENT
        e01100 = tax_unit("filer_e01100", period)
        c24510 = where(e01100 > 0, e01100, max_(0, dwks7) + e01100)
        return max_(0, c24510 - min_(0, tax_unit("filer_e58990", period)))


class dwks10(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "DWKS10"
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        dwks10_if_gains = add(tax_unit, period, ["dwks6", "dwks9"])
        dwks10_if_no_gains = max_(
            0,
            min_(
                tax_unit("filer_p23250", period),
                tax_unit("c23650", period),
            ),
        ) + tax_unit("filer_e01100", period)
        return where(
            tax_unit("hasqdivltcg", period),
            dwks10_if_gains,
            dwks10_if_no_gains,
        )


class dwks13(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "DWKS13"
    unit = USD
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )

    def formula(tax_unit, period, parameters):
        dwks1 = tax_unit("c04800", period)
        e24515 = tax_unit("filer_e24515", period)
        dwks11 = e24515 + tax_unit(
            "filer_e24518", period
        )  # Sch D lines 18 and 19, respectively
        dwks9 = tax_unit("dwks9", period)
        dwks12 = min_(dwks9, dwks11)
        dwks10 = tax_unit("dwks10", period)
        return (dwks10 - dwks12) * tax_unit("hasqdivltcg", period)


class dwks14(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "DWKS14"
    unit = USD
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )

    def formula(tax_unit, period, parameters):
        dwks1 = tax_unit("c04800", period)
        dwks13 = tax_unit("dwks13", period)
        return max_(0, dwks1 - dwks13) * tax_unit("hasqdivltcg", period)


class dwks19(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "DWKS14"
    unit = USD
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )

    def formula(tax_unit, period, parameters):
        dwks14 = tax_unit("dwks14", period)
        capital_gains = parameters(period).irs.capital_gains.brackets
        mars = tax_unit("mars", period)
        dwks1 = tax_unit("c04800", period)
        dwks16 = min_(capital_gains.thresholds["1"][mars], dwks1)
        dwks17 = min_(dwks14, dwks16)
        dwks10 = tax_unit("dwks10", period)
        dwks18 = max_(0, dwks1 - dwks10)
        return max_(dwks17, dwks18) * tax_unit("hasqdivltcg", period)


class fstax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


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


class filer_setax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employment tax for the tax unit (excluding dependents)"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("setax", tax_unit, period)


class aftertax_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "After-tax income"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        expanded = tax_unit("expanded_income", period)
        combined_tax = tax_unit("combined", period)
        return expanded - combined_tax


class benefit_value_total(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total benefit value"
    definition_period = YEAR
