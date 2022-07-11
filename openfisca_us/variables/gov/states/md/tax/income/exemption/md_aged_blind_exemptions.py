from openfisca_us.model_api import *


class md_aged_blind_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD aged blind exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Document/NF59A76006EA511E8ABBEE50DE853DFF4?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        filing_status_type = filing_status.possible_values

        blind = parameters(period).gov.states.md.tax.income.exemptions.blind
        # Count number of is_blind from tax_unit
        blind_head = tax_unit("blind_head", period) * 1
        blind_spouse = (
            (tax_unit("blind_spouse", period))
            & (filing_status == filing_status_type.JOINT)
        ) * 1

        blind_exemption_total = (blind_head + blind_spouse) * blind

        p = parameters(period).gov.states.md.tax.income.exemptions.aged

        age_for_exemption = p.age

        aged_amount = p.amount

        # TODO add aged exemptions
        aged_head = (tax_unit("age_head", period) >= age_for_exemption) * 1

        aged_spouse = (
            tax_unit("age_spouse", period) >= age_for_exemption * 1
        ) & (filing_status == filing_status_type.JOINT)

        aged_exemption_total = (
            aged_head * aged_amount + aged_spouse * aged_amount
        )

        # These apply to dependents over the age of 65
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)

        age = person("age", period)

        elderly = age >= age_for_exemption

        eligible = dependent & elderly

        aged_dependents = tax_unit.sum(dependent & elderly)

        aged_dependent_exemption = aged_dependents * p.aged_dependent

        return (
            blind_exemption_total
            + aged_exemption_total
            + aged_dependent_exemption
        )

    # Get blind exemption parameter
