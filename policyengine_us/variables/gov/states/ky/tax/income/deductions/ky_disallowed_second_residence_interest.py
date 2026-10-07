from policyengine_us.model_api import *


class ky_disallowed_second_residence_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky disallowed second-residence interest deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Federal qualified residence interest that Kentucky removes from "
        "itemized deductions once it limits the deduction to the principal "
        "residence. The federal deduction for mortgage interest and points "
        "is capped at the interest and points paid on the principal "
        "residence. The deprecated structured interest inputs count as "
        "principal-residence interest. Mortgage insurance premiums on the "
        "second residence are removed after the federal phase-out. The cap "
        "equals a recomputation on the principal residence alone when the "
        "combined debt is within the federal limit, or when both loans carry "
        "the same rate, fall under the same debt limit and carry points in "
        "proportion to their debt (or none). Otherwise it can differ in "
        "either direction, because the model does not record which loan "
        "secures which residence."
    )
    reference = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=57914#page=4",  # (2)(j)
        "https://apps.legislature.ky.gov/law/acts/26RS/documents/0161.pdf#page=13",
        "https://apps.legislature.ky.gov/law/acts/26RS/documents/0198.pdf#page=74",
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.deductions.itemized
        # Federal deductible interest and points on both qualified
        # residences, after the acquisition-debt limit.
        deductible_interest = tax_unit("deductible_mortgage_interest_tax_unit", period)
        # Interest and points paid on the principal residence.
        principal_residence_interest = (
            tax_unit("home_mortgage_interest_tax_unit", period)
            - add(tax_unit, period, ["second_residence_mortgage_interest"])
            + add(tax_unit, period, ["home_mortgage_points"])
        )
        second_residence_interest = add(
            tax_unit,
            period,
            ["second_residence_mortgage_interest", "second_residence_mortgage_points"],
        )
        # The excess can never exceed the second residence's own interest and
        # points, since the deductible pool is at most the sum of both.
        excess_interest = min_(
            second_residence_interest,
            max_(0, deductible_interest - principal_residence_interest),
        )
        # Premiums: the federal phase-out applies to all premiums alike, so
        # the second residence's part of the deduction is its share of them.
        second_residence_premiums = add(
            tax_unit, period, ["second_residence_mortgage_insurance_premiums"]
        )
        premiums = second_residence_premiums + add(
            tax_unit, period, ["mortgage_insurance_premiums"]
        )
        deductible_premiums = tax_unit("deductible_mortgage_insurance_premiums", period)
        second_residence_premium_share = np.divide(
            second_residence_premiums,
            premiums,
            out=np.zeros_like(premiums),
            where=premiums > 0,
        )
        disallowed = (
            excess_interest + deductible_premiums * second_residence_premium_share
        )
        return disallowed * p.principal_residence_interest_only
