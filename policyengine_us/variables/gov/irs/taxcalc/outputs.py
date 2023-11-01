from policyengine_us.model_api import *


class sey(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD

    adds = ["self_employment_income", "farm_income", "k1bx14"]


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


class sep(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    default_value = 1
    documentation = (
        "2 when filing_status is 3 (married filing separately); otherwise 1"
    )


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


class tax_unit_is_joint(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Joint-filing tax unit"
    documentation = "Whether this tax unit is a joint filer."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        return filing_status == filing_status.possible_values.JOINT
