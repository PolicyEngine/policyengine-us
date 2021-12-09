from openfisca_us.model_api import *


class snap_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "SNAP gross income"
    documentation = "Gross income for calculating SNAP eligibility"
    reference = "United States Code, Title 7, Section 2014(d)"
    unit = "currency-USD"

    def formula(spm_unit, period):
        return spm_unit.sum(spm_unit.members("market_income", period))


class snap_net_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Final net income, after all deductions"
    label = "SNAP net income"
    unit = "currency-USD"

    def formula(spm_unit, period, parameters):
        gross_income = spm_unit("snap_gross_income", period)
        deductions = spm_unit("snap_deductions", period)
        return gross_income - deductions
