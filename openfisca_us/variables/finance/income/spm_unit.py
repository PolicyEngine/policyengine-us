from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class SPM_unit_total_income(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit total income"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return spm_unit.sum(spm_unit.members("e00200", period))


class SPM_unit_SNAP(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit SNAP subsidy"
    definition_period = YEAR


class SPM_unit_capped_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit capped housing subsidy"
    definition_period = YEAR


class SPM_unit_school_lunch_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit school lunch subsidy"
    definition_period = YEAR


class SPM_unit_energy_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit school energy subsidy"
    definition_period = YEAR


class SPM_unit_WIC(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit WIC subsidy"
    definition_period = YEAR


class SPM_unit_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit net income"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        INCOME_COMPONENTS = [
            "SPM_unit_total_income",
            "SPM_unit_SNAP",
            "SPM_unit_capped_housing_subsidy",
            "SPM_unit_school_lunch_subsidy",
            "SPM_unit_energy_subsidy",
            "SPM_unit_WIC",
        ]
        EXPENSE_COMPONENTS = [
            "SPM_unit_FICA",
            "SPM_unit_federal_tax",
            "SPM_unit_state_tax",
            "SPM_unit_capped_work_childcare_expenses",
            "SPM_unit_medical_expenses",
        ]
        income = add(spm_unit, period, *INCOME_COMPONENTS)
        expense = add(spm_unit, period, *EXPENSE_COMPONENTS)
        return income - expense


class poverty_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = u"Poverty threshold"
    definition_period = YEAR


class in_poverty(Variable):
    value_type = bool
    entity = SPMUnit
    label = u"In poverty"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income = spm_unit("SPM_unit_net_income", period)
        poverty_threshold = spm_unit("poverty_threshold", period)
        return income < poverty_threshold
