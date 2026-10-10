from policyengine_us.model_api import *


class id_grocery_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7",
        # Idaho Code 63-3024A(1), (4): a credit for the taxpayer, the spouse and
        # each IRC 152 dependent claimed on the return, never two for the same
        # personal exemption.
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3024A/",
        # 2025 Form 40 instructions, line 43 and the Food Tax Credit
        # Worksheet (yourself, spouse, dependents).
        # PDF pages 13-14
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=13",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        qualified_months = person("id_grocery_credit_qualified_months", period)
        p = parameters(period).gov.states.id.tax.income.credits.grocery.aged
        if p.in_effect:
            full_amount = add(
                person,
                period,
                ["id_grocery_credit_base", "id_grocery_credit_aged"],
            )
        else:
            full_amount = person("id_grocery_credit_base", period)
        # A filer whom another taxpayer can claim gets no credit ("You can't
        # claim this credit if someone else, such as a parent, can claim you
        # as a dependent"); the other spouse on a joint return keeps theirs.
        # A return on which the filer (or, if joint, either spouse) can be
        # claimed has no dependents (IRC 152(b)(1)).
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        eligible = where(filer, ~claimed, ~filer_is_dependent)
        credit_value = full_amount * (qualified_months / MONTHS_IN_YEAR) * eligible
        return tax_unit.sum(credit_value)
