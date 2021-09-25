from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class SPM_unit_FICA(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit total FICA"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return sum_contained_tax_units("employee_payrolltax", spm_unit, period)


class SPM_unit_federal_tax(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit federal tax"
    definition_period = YEAR


class SPM_unit_state_tax(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit state tax"
    definition_period = YEAR


class SPM_unit_capped_work_childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit work and childcare expenses"
    definition_period = YEAR


class SPM_unit_medical_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit medical expenses"
    definition_period = YEAR
