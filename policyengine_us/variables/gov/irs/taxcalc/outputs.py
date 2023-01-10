from policyengine_us.model_api import *


class sey(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD

    adds = ["self_employment_income", "farm_income", "k1bx14"]


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

    adds = [
        # Tax unit level.
        "iitax",
        "additional_medicare_tax",
        # Person level
        "self_employment_medicare_tax",
        "self_employment_social_security_tax",
        "employee_medicare_tax",
        "employee_social_security_tax",
    ]


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
        return max_(0, tax_unit_non_dep_sum("earned", tax_unit, period))


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
        misc = parameters(period).gov.irs.ald.misc
        adjustment = (
            (1 - misc.self_emp_tax_adj)
            * misc.employer_share
            * person("self_employment_tax", period)
        )
        return person("earned_income", period) - adjustment


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
    documentation = (
        "2 when filing_status is 3 (married filing separately); otherwise 1"
    )


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


tax_unit_net_capital_gains = variable_alias(
    "tax_unit_net_capital_gains", c01000
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
        misc = parameters(period).gov.irs.ald.misc
        setax = add(tax_unit, period, ["self_employment_tax"])
        return (1 - misc.self_emp_tax_adj) * misc.employer_share * setax


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
        filing_status = tax_unit("filing_status", period)
        return filing_status == filing_status.possible_values.JOINT


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


class benefit_value_total(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total benefit value"
    definition_period = YEAR
