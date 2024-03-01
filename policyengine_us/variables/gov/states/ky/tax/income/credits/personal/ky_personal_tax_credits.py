from policyengine_us.model_api import *


class ky_personal_tax_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky personal tax credits combined"
    unit = USD
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3"  # (3) (a)
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        ky_files_separately = tax_unit("ky_files_separately", period)
        person = tax_unit.members
        ky_personal_tax_credits_indiv = person(
            "ky_personal_tax_credits_indiv", period
        )
        ky_personal_tax_credits_joint = person(
            "ky_personal_tax_credits_joint", period
        )
        return where(
            ky_files_separately,
            tax_unit.sum(ky_personal_tax_credits_indiv),
            tax_unit.sum(ky_personal_tax_credits_joint),
        )
