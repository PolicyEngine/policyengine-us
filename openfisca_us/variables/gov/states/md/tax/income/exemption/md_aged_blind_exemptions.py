from openfisca_us.model_api import *
from build.lib.openfisca_us.variables.irs.inputs import age_head


class md_aged_blind_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD aged blind exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Document/NF59A76006EA511E8ABBEE50DE853DFF4?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"

    def formula(tax_unit, period, parameters):
        blind = parameters(period).gov.states.md.tax.income.exemptions.blind
        # Count number of is_blind from tax_unit
        blind_head = tax_unit("blind_head", period) * 1
        blind_spouse = tax_unit("blind_spouse", period) * 1
        blind_exemption_total = (blind_head + blind_spouse) * blind

        p = parameters(period).gov.states.md.tax.income.exemptions.aged
        age_for_exemption = p.age
        aged_amount = p.amount
        # TODO add aged exemptions
        aged_head = tax_unit("age_head", period) >= age_for_exemption * 1
        aged_spouse = tax_unit("age_spouse", period) >= age_for_exemption * 1

        aged_exemption_total = (
            aged_head * aged_amount + aged_spouse * aged_amount
        )

        # These apply to dependents over the age of 65
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        elderly = age >= age_for_exemption
        eligible = dependent & (elderly)
        count_eligible = tax_unit.sum(eligible)
        aged_dependent_exemption = count_eligible * p.aged_dependent

        return (
            blind_exemption_total
            + aged_exemption_total
            + aged_dependent_exemption
        )

    # Get blind exemption parameter
