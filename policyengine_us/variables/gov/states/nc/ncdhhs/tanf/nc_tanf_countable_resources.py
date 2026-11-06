from policyengine_us.model_api import *


class nc_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF countable resources"
    unit = USD
    definition_period = YEAR
    quantity_type = STOCK
    reference = (
        "https://regulations.justia.com/states/north-carolina/title-10a/chapter-71/subchapter-w/section-0400/section-71w-0407",
        "https://policies.ncdhhs.gov/wp-content/uploads/wf115.pdf#page=2",
    )
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        # Work First counts cash, checking and savings accounts, stocks, bonds and
        # mutual fund shares; motor vehicles, real property and retirement accounts
        # do not count (Work First Manual, section 115, II).
        return spm_unit("spm_unit_cash_assets", period.this_year)
