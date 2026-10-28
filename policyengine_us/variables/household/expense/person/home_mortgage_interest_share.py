from policyengine_us.model_api import *


class home_mortgage_interest_share(Variable):
    value_type = float
    entity = Person
    label = "Share of tax-unit home mortgage interest"
    definition_period = YEAR
    documentation = (
        "Allocates the tax unit's mortgage interest and points (and their "
        "deductible and non-deductible parts) to the filers: in proportion "
        "to the head's and spouse's own reported interest and points on both "
        "residences, or evenly between them when only other members (such "
        "as dependents) report them. Shares sum to one across head and "
        "spouse, so the person amounts add back to the tax-unit totals."
    )

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        reported_interest = head_or_spouse * add(
            person,
            period,
            [
                "home_mortgage_interest",
                "home_mortgage_points",
                "second_residence_mortgage_interest",
                "second_residence_mortgage_points",
            ],
        )
        total_reported_interest = person.tax_unit.sum(reported_interest)

        reported_share = np.zeros_like(total_reported_interest)
        reported_mask = total_reported_interest > 0
        reported_share[reported_mask] = (
            reported_interest[reported_mask] / total_reported_interest[reported_mask]
        )

        filer_count = person.tax_unit.sum(head_or_spouse)
        equal_share = np.zeros_like(filer_count)
        filer_mask = filer_count > 0
        equal_share[filer_mask] = head_or_spouse[filer_mask] / filer_count[filer_mask]

        return where(total_reported_interest > 0, reported_share, equal_share)
