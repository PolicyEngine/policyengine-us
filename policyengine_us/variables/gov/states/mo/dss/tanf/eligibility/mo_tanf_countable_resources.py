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
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-35/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Per DSS Manual 0210.005.10, an SSI participant's resources are
        # excluded along with their needs and income ("Exclude the
        # expenses, income, and resources"). The excluded people's share is
        # subtracted from the unit aggregate rather than the total being
        # rebuilt from person-level values, so households that supply only
        # the spm_unit_cash_assets aggregate keep the aggregate behavior;
        # the exclusion activates when assets are attributed to people
        # through the person-level components of spm_unit_cash_assets.
        total = spm_unit("spm_unit_cash_assets", period.this_year)
        person = spm_unit.members
        is_ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        # 13 CSR 40-2.310(3) counts the resources of a needy non-parent
        # caretaker relative or legal guardian only "if included in the
        # grant" (DSS Manual 0210.005.35: "If an NPCR is found to be needy
        # and is included in the assistance group, count the NPCR's
        # resources"). The caretaker's spouse is not a listed member, so
        # their resources are excluded in every case.
        npcr_family = person("mo_tanf_non_parent_caretaker_budget_member", period)
        member = person("mo_tanf_is_assistance_unit_member", period)
        excluded = is_ssi_recipient | (npcr_family & ~member)
        # This component list must mirror spm_unit_cash_assets.adds: the
        # subtraction below assumes the person-level components sum to the
        # unit aggregate, so a divergence would under- or over-subtract.
        person_assets = add(
            person,
            period.this_year,
            ["bank_account_assets", "stock_assets", "bond_assets"],
        )
        excluded_assets = spm_unit.sum(person_assets * excluded)
        return max_(total - excluded_assets, 0)
