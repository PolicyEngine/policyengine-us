from policyengine_us.model_api import *


class mt_capital_loss_reallocation(Variable):
    value_type = float
    entity = Person
    label = "Montana reallocation of the capital loss deduction between spouses"
    unit = USD
    documentation = (
        "Each spouse's federal part of the capital loss deduction "
        "(limited_capital_loss_person) less their part under Montana's rule "
        "for spouses who file separately: a loss clearly attributable to one "
        "spouse goes on that spouse's return, and otherwise the loss is split "
        "equally. Adding this to a spouse's federal AGI gives the AGI Montana "
        "uses for that spouse. The amounts add up to zero over the couple."
    )
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # MCA 15-30-2110(6) (2021), in force through tax year 2023.
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0100/0150-0300-0210-0100.html",
    )

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_loss = head_or_spouse & (person("capital_losses", period) > 0)
        spouses_with_loss = person.tax_unit.sum(has_loss)
        head_spouse_count = person.tax_unit("head_spouse_count", period)
        limited_capital_loss = person.tax_unit("limited_capital_loss", period)
        equal_part = np.divide(
            head_or_spouse * limited_capital_loss,
            head_spouse_count,
            out=np.zeros_like(limited_capital_loss, dtype=float),
            where=head_spouse_count > 0,
        )
        montana_part = where(
            spouses_with_loss == 1,
            has_loss * limited_capital_loss,
            equal_part,
        )
        return person("limited_capital_loss_person", period) - montana_part
