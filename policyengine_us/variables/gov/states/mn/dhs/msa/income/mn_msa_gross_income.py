from policyengine_us.model_api import *


class mn_msa_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid gross income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
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
                "ssi_earned_income",
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
            income += min_(wages, premiums) / MONTHS_IN_YEAR

        # CM 0017 substitutes the full FBR for an SSI recipient's payment.
        ssi = person("ssi", period)
        ssi_fbr = person("ssi_amount_if_eligible", period)
        return income + where(ssi > 0, ssi_fbr, 0)
