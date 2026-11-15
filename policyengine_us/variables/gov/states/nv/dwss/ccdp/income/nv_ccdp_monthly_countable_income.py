from policyengine_us.model_api import *


class nv_ccdp_monthly_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada CCDP monthly countable income, rounded to the nearest dollar"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NV
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=75"

    def formula(spm_unit, period, parameters):
        # MS 316, second step: round gross monthly income to the nearest dollar,
        # with 50 cents and up rounding up. Round to cents first so floating-point
        # noise from dividing the annual amount can't move a half dollar.
        monthly_income = (
            spm_unit("nv_ccdp_countable_income", period.this_year) / MONTHS_IN_YEAR
        )
        return np.floor(np.round(monthly_income, 2) + 0.5)
