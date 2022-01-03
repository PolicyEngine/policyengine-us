from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.spm_unit import *


class tanf(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF"
    documentation = (
        "Amount of Temporary Assistance for Needy Families benefit received."
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        # Obtain eligibility.
        eligible = spm_unit("is_tanf_eligible", period)
        # Obtain amount they would receive if they were eligible.
        amount_if_eligible = spm_unit("tanf_amount_if_eligible", period)
        return where(eligible, amount_if_eligible, 0)


class continuous_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Continued Economic Eligibility for TANF"
    documentation = "Whether the familiy meets the economic requirements for the Temporary Assistance for Needy Families program after being approved."


class initial_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Initial Economic Eligibility for TANF"
    documentation = "Whether the familiy meets the economic requirements for the Temporary Assistance for Needy Families program on application."

    def formula(spm_unit, period, parameters):
        ied = spm_unit('tanf_initial_employment_deduction', period)
        earned_income = spm_unit('tanf_gross_earned_income', period)
        net_earned_income = earned_income - ied
        payment_level = spm_unit('tanf_max_amount', period)
        return net_earned_income <= payment_level

class is_person_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person-level eligiblity for TANF based on age, pregnancy, etc."
    documentation = "Whether a person in a family applying for the Temporary Assistance for Needy Families program meets demographic requirements."

    def formula(person, period, parameters):
        child_0_17 = person("is_child", period)
        is_18 = person("age", period) == 18
        school_enrolled_18_year_old = person("is_in_school", period) & is_18
        pregnant = person("is_pregnant", period)
        return child_0_17 | school_enrolled_18_year_old | pregnant


class is_tanf_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Current Enrollement in TANF"
    documentation = "Whether the familiy is currently enrolled in the Temporary Assistance for Needy Families program."


class is_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligibility for TANF"
    documentation = "Whether the family is eligible for Temporary Assistance for Needy Families benefit."

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit.any(
            spm_unit.members("is_person_demographic_tanf_eligible", period)
        )
        economic_eligible = where(
            spm_unit("is_tanf_enrolled", period),
            spm_unit("continuous_tanf_eligibility", period),
            spm_unit("initial_tanf_eligibility", period),
        )
        return demographic_eligible & economic_eligible


class tanf_max_amount(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF maximum benefit"
    documentation = "The maximum benefit amount a family could receive from Temporary Assistance for Needy Families given their state and family size."
    unit = USD

    def formula(spm_unit, period, parameters):
        family_size = spm_unit.nb_persons().astype(str)
        state = spm_unit.household("state_code_str", period)
        max_amount = parameters(period).hhs.tanf.max_amount
        return max_amount[state][family_size] * 12


class tanf_initial_employment_deduction(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF IED (Initial Employment Deduction)"
    documentation = "The amount deducted from the countable earnings of a TANF application when calculating initial eligibility."
    unit = USD

    def formula(spm_unit, period, parameters):
        family_size = spm_unit.nb_persons().astype(str)
        state = spm_unit.household("state_code_str", period)
        ied = parameters(period).hhs.tanf.initial_employment_deduction
        return ied[state][family_size] * 12


class tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF countable income"
    documentation = "Countable income for calculating Temporary Assistance for Needy Families benefit."
    unit = USD

    def formula(spm_unit, period, parameters):
        earned_income = spm_unit("tanf_gross_earned_income", period)
        state = spm_unit.household("state_code_str", period)
        earned_income_deduction = parameters(
            period
        ).hhs.tanf.earned_income_deduction
        return earned_income * (1 - earned_income_deduction[state])


class tanf_total_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF gross income"
    documentation = "Gross income for calculating Temporary Assistance for Needy Families benefit. Includes both gross earned and unearned income."
    unit = USD
    reference = "https://www.dhs.state.il.us/page.aspx?item=15814"

    def formula(spm_unit, period, parameters):
        return add(spm_unit, period, "tanf_gross_earned_income", "tanf_gross_unearned_income")

class tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF gross earned income"
    documentation = "Gross earned income for calculating Temporary Assistance for Needy Families benefit."
    unit = USD
    reference = "https://www.dhs.state.il.us/page.aspx?item=15814"

    def formula(spm_unit, period, parameters):
        return spm_unit.sum(spm_unit.members("market_income", period))


class tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF gross unearned income"
    documentation = "Gross unearned income for calculating Temporary Assistance for Needy Families benefit."
    unit = USD
    reference = "https://www.dhs.state.il.us/page.aspx?item=15814"

    def formula(spm_unit, period, parameters):
        return spm_unit("ssi", period)

class tanf_amount_if_eligible(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF amount if family is eligible"
    documentation = "How much a family would receive if they were eligible for Temporary Assistance for Needy Families benefit."
    unit = USD

    def formula(spm_unit, period, parameters):
        max_amount = spm_unit("tanf_max_amount", period)
        countable_income = spm_unit("tanf_countable_income", period)
        return max_(0, max_amount - countable_income)
