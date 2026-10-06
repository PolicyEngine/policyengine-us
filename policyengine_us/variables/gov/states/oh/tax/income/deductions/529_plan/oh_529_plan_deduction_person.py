from policyengine_us.model_api import *


class oh_529_plan_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio deduction for contributions to 529 plans"
    unit = USD
    documentation = (
        "The tax unit's Ohio 529 deduction, shared between the head and spouse "
        "in proportion to their own contributions; the head takes it when "
        "neither contributed this year, as for a deduction of carried-forward "
        "contributions. A dependent's contributions are their own, deducted "
        "on their own return, so a dependent gets none."
    )
    definition_period = YEAR
    reference = (
        # R.C. 5747.70(A): the deduction is "allowed to a taxpayer who
        # contributes".
        "https://codes.ohio.gov/assets/laws/revised-code/authenticated/57/5747/5747.70/4-3-2023/5747.70-4-3-2023.pdf#page=1",
        # 2025 IT 1040 instructions, line 37: "You may not deduct ... Amounts
        # contributed by another person."
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        filer = ~person("is_tax_unit_dependent", period)
        contributions = person("investment_in_529_plan_indv", period) * filer
        total_contributions = person.tax_unit.sum(contributions)
        share = np.divide(
            contributions,
            total_contributions,
            out=np.zeros_like(total_contributions, dtype=float),
            where=total_contributions > 0,
        )
        share = where(
            total_contributions > 0, share, person("is_tax_unit_head", period)
        )
        return share * person.tax_unit("oh_529_plan_deduction", period)
