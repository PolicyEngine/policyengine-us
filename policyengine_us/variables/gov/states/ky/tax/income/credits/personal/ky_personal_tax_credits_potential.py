from policyengine_us.model_api import *


class ky_personal_tax_credits_potential(Variable):
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
        # Under the combined-separate election, each spouse's personal credits
        # offset only their own column's tax and floor at zero (Form 740 lines
        # 16-18), so cap each person's credit at their own pre-credit tax
        # before summing rather than pooling across columns.
        indiv_credits = person("ky_personal_tax_credits_indiv", period)
        indiv_tax = person("ky_income_tax_before_non_refundable_credits_indiv", period)
        capped_indiv_credits = min_(indiv_credits, indiv_tax)
        ky_personal_tax_credits_joint = person("ky_personal_tax_credits_joint", period)
        return where(
            ky_files_separately,
            tax_unit.sum(capped_indiv_credits),
            tax_unit.sum(ky_personal_tax_credits_joint),
        )
