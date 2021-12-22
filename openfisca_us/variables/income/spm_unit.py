from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class spm_unit_total_income(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit total income"
    definition_period = YEAR
    unit = "currency-USD"


class spm_unit_snap(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit SNAP subsidy"
    definition_period = YEAR
    unit = "currency-USD"


class spm_unit_capped_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit capped housing subsidy"
    definition_period = YEAR
    unit = "currency-USD"


class spm_unit_school_lunch_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit school lunch subsidy"
    definition_period = YEAR
    unit = "currency-USD"


class spm_unit_energy_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit school energy subsidy"
    definition_period = YEAR
    unit = "currency-USD"


class spm_unit_wic(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit WIC subsidy"
    definition_period = YEAR
    unit = "currency-USD"


class spm_unit_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit net income"
    definition_period = YEAR
    unit = "currency-USD"

    def formula(spm_unit, period, parameters):
        INCOME_COMPONENTS = [
            "spm_unit_total_income",
            "spm_unit_snap",
            "spm_unit_capped_housing_subsidy",
            "spm_unit_school_lunch_subsidy",
            "spm_unit_energy_subsidy",
            "spm_unit_wic",
        ]
        EXPENSE_COMPONENTS = [
            "spm_unit_fica",
            "spm_unit_federal_tax",
            "spm_unit_state_tax",
            "spm_unit_capped_work_childcare_expenses",
            "spm_unit_medical_expenses",
        ]
        income = add(spm_unit, period, *INCOME_COMPONENTS)
        expense = add(spm_unit, period, *EXPENSE_COMPONENTS)
        return income - expense


class spm_unit_spm_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit's SPM poverty threshold"
    definition_period = YEAR
    unit = "currency-USD"


class spm_unit_is_in_spm_poverty(Variable):
    value_type = bool
    entity = SPMUnit
    label = u"SPM unit in SPM poverty"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income = spm_unit("spm_unit_net_income", period)
        poverty_threshold = spm_unit("spm_unit_spm_threshold", period)
        return income < poverty_threshold


class experienced_covid_income_loss(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Experienced Covid income loss"
    documentation = "Whether the SPM unit experienced a loss of income due to COVID-19 since February 2020"
    definition_period = YEAR
