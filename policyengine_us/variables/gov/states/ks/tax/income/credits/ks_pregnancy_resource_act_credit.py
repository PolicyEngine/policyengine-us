from policyengine_us.model_api import *


class ks_pregnancy_resource_act_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas pregnancy resource act tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://ksrevisor.gov/statutes/chapters/ch79/079_032_0316.html",
        "https://www.ksrevenue.gov/prtaxcredits-pregnancy.html",
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ks.tax.income.credits.pregnancy_resource_act
        # Kansas allows a credit equal to 70% of contributions to eligible
        # pregnancy resource organizations. We use charitable_cash_donations
        # as a simplified proxy since we cannot model specific organization
        # donations. In reality, taxpayers must contribute to organizations
        # approved by the Kansas Department of Revenue.
        #
        # The credit is capped at the org_cap per organization per taxpayer,
        # but since we cannot track individual organization contributions,
        # we apply the per-org cap as an overall limit on qualifying donations.
        charitable_donations = add(
            tax_unit, period, ["charitable_cash_donations"]
        )
        # Apply the per-organization cap as a simplified limit
        capped_donations = min_(charitable_donations, p.org_cap)
        # Calculate credit as rate times capped donations
        return capped_donations * p.rate
