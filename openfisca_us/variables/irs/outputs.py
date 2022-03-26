from openfisca_us.model_api import *


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


class c05700(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


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


class tax_unit_is_joint(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Joint-filing tax unit"
    documentation = "Whether this tax unit is a joint filer."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        mars = tax_unit("mars", period)
        return mars == mars.possible_values.JOINT


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


class fstax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD


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
