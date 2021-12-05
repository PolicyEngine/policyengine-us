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
    unit = "currency-USD"

    def formula(spm_unit, period, parameters):
        # Obtain eligibility.
        eligible = spm_unit("is_tanf_eligible", period)
        # Obtain amount they would receive if they were eligible.
        amount_if_eligible = spm_unit("tanf_amount_if_eligible", period)
        return where(eligible, amount_if_eligible, 0)


class is_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligibility for TANF"
    documentation = "Whether the family is eligible for Temporary Assistance for Needy Families benefit."

    def formula(spm_unit, period, parameters):
        children_0_17 = spm_unit.sum(spm_unit.members("is_child", period))
        school_enrolled_18_year_olds = spm_unit.sum(
            (spm_unit.members("is_in_school", period))
            & (spm_unit.members("age", period) == 18)
        )
        pregnant_people = spm_unit.sum(spm_unit.members("is_pregnant", period))
        return (
            children_0_17 + school_enrolled_18_year_olds + pregnant_people
        ) > 0


# Quick fix, should be fixed by resolving https://github.com/openfisca/openfisca-core/issues/1085
class state_code_str(Variable):
    value_type = str
    entity = Household
    definition_period = ETERNITY

    def formula(household, period):
        return household("state_code", period).decode_to_str()


class tanf_max_amount(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF maximum benefit"
    documentation = "The maximum benefit amount a family could receive from Temporary Assistance for Needy Families given their state and family size."
    unit = "currency-USD"

    def formula(spm_unit, period, parameters):
        family_size = spm_unit.nb_persons().astype(str)
        state = spm_unit.household("state_code_str", period)
        max_amount = parameters(period).hhs.tanf.max_amount
        return max_amount[state][family_size] * 12


class tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF countable income"
    documentation = "Countable income for calculating Temporary Assistance for Needy Families benefit."
    unit = "currency-USD"


class tanf_amount_if_eligible(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF amount if family is eligible"
    documentation = "How much a family would receive if they were eligible for Temporary Assistance for Needy Families benefit."
    unit = "currency-USD"

    def formula(spm_unit, period, parameters):
        max_amount = spm_unit("tanf_max_amount", period)
        countable_income = spm_unit("tanf_countable_income", period)
        return max_(0, max_amount - countable_income)
