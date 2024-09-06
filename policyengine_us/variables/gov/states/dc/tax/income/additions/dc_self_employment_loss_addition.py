from policyengine_us.model_api import *


class dc_self_employment_loss_addition(Variable):
    value_type = float
    entity = Person
    label = "DC excess self-employment loss addition"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        loss_person = max_(0, -person("self_employment_income", period))
        loss_taxunit = person.tax_unit.sum(loss_person)
        p = parameters(period).gov.states.dc.tax.income.additions
        addition_taxunit = max_(
            0, loss_taxunit - p.self_employment_loss.threshold
        )
        # allocate taxunit addition in proportion to head and spouse losses
        filing_status = person.tax_unit("filing_status", period)
        is_joint = filing_status == filing_status.possible_values.JOINT
        loss_fraction = np.zeros_like(loss_person)
        mask = loss_taxunit > 0
        loss_fraction[mask] = loss_person[mask] / loss_taxunit[mask]
        addition_fraction = where(is_joint, loss_fraction, 1)
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        return (is_head | is_spouse) * addition_taxunit * addition_fraction
