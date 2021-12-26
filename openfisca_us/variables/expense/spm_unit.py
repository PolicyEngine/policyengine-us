from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class spm_unit_fica(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit total FICA"
    definition_period = YEAR
    unit = "currency-USD"

    def formula(spm_unit, period, parameters):
        return sum_contained_tax_units("employee_payrolltax", spm_unit, period)


class spm_unit_federal_tax(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit federal tax"
    definition_period = YEAR
    unit = "currency-USD"


class spm_unit_state_tax(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit state tax"
    definition_period = YEAR
    unit = "currency-USD"


class spm_unit_capped_work_childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit work and childcare expenses"
    definition_period = YEAR
    unit = "currency-USD"


class spm_unit_medical_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit medical expenses"
    definition_period = YEAR
    unit = "currency-USD"


class housing_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing cost"
    documentation = "Housing cost for this SPM unit"
    unit = "currency-USD"
    definition_period = YEAR


class broadband_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Broadband cost"
    documentation = "Broadband cost for this SPM unit"
    unit = "currency-USD"
    definition_period = YEAR


class phone_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Phone cost"
    documentation = "Phone line cost for this SPM unit"
    unit = "currency-USD"
    definition_period = YEAR
