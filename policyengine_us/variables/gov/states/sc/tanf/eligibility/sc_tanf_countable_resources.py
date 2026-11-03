from policyengine_us.model_api import *


class sc_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF countable resources"
    unit = USD
    definition_period = MONTH
    quantity_type = STOCK
    defined_for = StateCode.SC
    # PDF pages 56, 91, 117
    reference = "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=56"  # Sections 3.6, 6.4 and 7.7

    def formula(spm_unit, period, parameters):
        # Sections 3.6 and 7.7 exclude the SSI recipient's resources along
        # with his or her income and needs. The excluded people's assets are
        # subtracted from the unit aggregate rather than the total being
        # rebuilt from person-level values, so households that supply only
        # the spm_unit_cash_assets aggregate keep the aggregate behavior.
        total = spm_unit("spm_unit_cash_assets", period.this_year)
        person = spm_unit.members
        ssi_recipient = person("sc_tanf_ssi_recipient", period)
        # This component list must mirror spm_unit_cash_assets.adds, so the
        # subtraction removes exactly the excluded members' share.
        person_assets = add(
            person,
            period.this_year,
            ["bank_account_assets", "stock_assets", "bond_assets"],
        )
        excluded_assets = spm_unit.sum(person_assets * ssi_recipient)
        return max_(total - excluded_assets, 0)
