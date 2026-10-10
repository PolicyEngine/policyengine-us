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
    )

    def formula(tax_unit, period, parameters):
        # § 10-709(a)(2): the poverty income standard "that corresponds to the
        # number of exemptions which the individual is allowed and claims
        # under § 10-211(b)(1)". That is the tax unit's size unless a filer
        # can be claimed as a dependent, in which case only the filers who
        # cannot be claimed count and there are no dependents (IRC 152(b)(1)).
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        exemptions = tax_unit("exemptions_count", period)
        state_group = tax_unit.household("state_group_str", period)
        return where(
            filer_is_dependent,
            fpg(exemptions, state_group, period, parameters),
            tax_unit("tax_unit_fpg", period),
        )
