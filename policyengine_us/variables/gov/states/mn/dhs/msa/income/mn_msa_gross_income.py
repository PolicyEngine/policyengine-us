from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class mn_msa_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid gross income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    # Section 256D.35 directly defines MSA gross income. Rule 9500.1206
    # describes GA conventions, which CM 0017 adopts for non-SSI recipients.
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.35#stat.256D.35.10",
        "https://www.revisor.mn.gov/rules/9500.1206/#rule.9500.1206.15a",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=cm_0017",
    )

    def formula(person, period, parameters):
        income = add(
            person,
            period,
            [
                "ssi_earned_income_after_spousal_loss",
                "ssi_unearned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_parent",
            ],
        )
        # MSA gross income is measured before deductions and disregards.
        # Its net-income calculation adopts SSI exclusions (256D.435),
        # but the gross test and guardian-fee cap must restore the employee's
        # salary-reduction premium excluded from their own SSI wages.
        # Keep the SSI financial-responsibility rules for deemed income.
        sources = parameters(period).gov.ssa.ssi.income.sources.earned
        if "employment_income" in sources:
            wages = max_(person("employment_income", period.this_year), 0)
            premiums = max_(
                person("pre_tax_health_insurance_premiums", period.this_year), 0
            )
            restoration = min_(wages, premiums)
            earned = person("ssi_earned_income", period.this_year)
            if np.any(earned < 0):
                spouse = _ssi_spouse_index(person, period.this_year)
                safe_spouse = np.maximum(spouse, 0)
                spouse_earned = where(spouse >= 0, earned[safe_spouse], 0)
                spouse_restoration = where(spouse >= 0, restoration[safe_spouse], 0)
                # Restore premiums before flooring the gross earned pool.
                # Losses already absorbed by a spouse's positive SSI earnings
                # must not be deducted twice. Any remaining loss absorbs own
                # premiums first, then the spouse's, just as other earnings do.
                own_loss = max_(-earned - max_(spouse_earned, 0), 0)
                spouse_loss = max_(-spouse_earned - max_(earned, 0), 0)
                restoration = max_(
                    restoration - own_loss - max_(spouse_loss - spouse_restoration, 0),
                    0,
                )
            income += restoration / MONTHS_IN_YEAR

        # CM 0017 substitutes the full FBR for an SSI recipient's payment.
        ssi = person("ssi", period)
        ssi_fbr = person("ssi_amount_if_eligible", period)
        return income + where(ssi > 0, ssi_fbr, 0)
