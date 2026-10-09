from policyengine_us.model_api import *


class dc_self_employment_loss_addition(Variable):
    value_type = float
    entity = Person
    label = "DC excess self-employment loss addition"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55",
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        # Only the head's and spouse's losses are on this return. A tax-unit
        # dependent's losses are not in loss_ald, so counting them would raise
        # the addition or dilute the filers' shares of it.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        loss_person = is_head_or_spouse * max_(
            0, -person("total_self_employment_income", period)
        )
        loss_taxunit = person.tax_unit.sum(loss_person)
        # Cap at the business losses actually deducted in federal AGI: loss_ald
        # less its capital loss parts (self-employment, farm, rental,
        # partnership, estate and other business losses after section 461(l)).
        loss_ald = person.tax_unit("loss_ald", period)
        capital_loss_in_ald = add(
            person.tax_unit,
            period,
            ["capital_losses_allowed_against_gains", "limited_capital_loss"],
        )
        business_loss_in_ald = max_(0, loss_ald - capital_loss_in_ald)
        effective_loss = min_(loss_taxunit, business_loss_in_ald)
        p = parameters(period).gov.states.dc.tax.income.additions
        addition_taxunit = max_(0, effective_loss - p.self_employment_loss.threshold)
        # allocate taxunit addition in proportion to head and spouse losses
        filing_status = person.tax_unit("filing_status", period)
        is_joint = filing_status == filing_status.possible_values.JOINT
        loss_fraction = np.zeros_like(loss_person)
        mask = loss_taxunit > 0
        loss_fraction[mask] = loss_person[mask] / loss_taxunit[mask]
        addition_fraction = where(is_joint, loss_fraction, 1)
        return is_head_or_spouse * addition_taxunit * addition_fraction
