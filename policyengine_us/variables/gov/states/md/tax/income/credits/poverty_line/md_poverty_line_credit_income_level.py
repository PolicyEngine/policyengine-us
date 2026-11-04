from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class md_poverty_line_credit_income_level(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland poverty line credit applicable poverty income level"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-709&enactments=false",
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-211&enactments=false",
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=23",
    )

    def formula(tax_unit, period, parameters):
        # § 10-709(a)(2): the poverty income standard "that corresponds to the
        # number of exemptions which the individual is allowed and claims
        # under § 10-211(b)(1)". That is the tax unit's size unless a filer
        # can be claimed as a dependent, in which case only the filers who
        # cannot be claimed count, with dependents only under the claimant
        # filing exception (IRC 152(b)(1)).
        # HHS lists guideline amounts from one person up, so no amount
        # corresponds to zero exemptions: a filer with no allowed exemption
        # has no applicable poverty income level. The 2025 Resident Booklet
        # likewise bars every filing status 6 filer from the credit.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        exemptions = tax_unit("md_personal_exemptions_count", period)
        state_group = tax_unit.household("state_group_str", period)
        dependent_filer_level = where(
            exemptions > 0,
            fpg(exemptions, state_group, period, parameters),
            0,
        )
        return where(
            filer_is_dependent,
            dependent_filer_level,
            tax_unit("tax_unit_fpg", period),
        )
