from policyengine_us.model_api import *


class mo_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF countable resources"
    unit = USD
    definition_period = MONTH
    quantity_type = STOCK
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-10/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Per DSS Manual 0210.005.10, an SSI participant's resources are
        # excluded along with their needs and income ("Exclude the
        # expenses, income, and resources"). The SSI recipients' share is
        # subtracted from the unit aggregate rather than the total being
        # rebuilt from person-level values, so households that supply only
        # the spm_unit_cash_assets aggregate keep the aggregate behavior;
        # the exclusion activates when assets are attributed to people
        # through the person-level components of spm_unit_cash_assets.
        total = spm_unit("spm_unit_cash_assets", period.this_year)
        person = spm_unit.members
        is_ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        # This component list must mirror spm_unit_cash_assets.adds: the
        # subtraction below assumes the person-level components sum to the
        # unit aggregate, so a divergence would under- or over-subtract.
        person_assets = add(
            person,
            period.this_year,
            ["bank_account_assets", "stock_assets", "bond_assets"],
        )
        ssi_recipient_assets = spm_unit.sum(person_assets * is_ssi_recipient)
        return max_(total - ssi_recipient_assets, 0)
