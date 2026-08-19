from policyengine_us.model_api import *


class ca_sbd_general_relief_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets San Bernardino County General Relief resource requirements"
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sbd.general_relief.resources
        # Resources are year-defined stocks; read them with period.this_year
        # so this monthly formula does not divide balances across months.
        # Real property is the combined assessed value with no encumbrances
        # deducted. The county's rule evaluating a vehicle used as a
        # principal residence under this limit is not modeled — vehicles
        # are always evaluated under the personal property test.
        real_property = add(spm_unit, period.this_year, ["assessed_property_value"])
        real_property_eligible = real_property <= p.real_property_limit
        countable_resources = spm_unit(
            "ca_sbd_general_relief_countable_resources", period.this_year
        )
        personal_property_eligible = countable_resources <= p.personal_property_limit
        # Liquid assets (cash, bank accounts, stocks, and bonds) may not
        # exceed the limit, modeled as a flat per-assistance-unit amount.
        liquid_assets = spm_unit("spm_unit_cash_assets", period.this_year)
        liquid_asset_eligible = liquid_assets <= p.liquid_asset_limit
        return (
            real_property_eligible & personal_property_eligible & liquid_asset_eligible
        )
