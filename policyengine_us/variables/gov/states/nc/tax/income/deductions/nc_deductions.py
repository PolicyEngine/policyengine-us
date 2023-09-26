from policyengine_us.model_api import *


class nc_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions"
    defined_for = StateCode.NC

    adds = "gov.states.nc.tax.income.deductions.deductions"
