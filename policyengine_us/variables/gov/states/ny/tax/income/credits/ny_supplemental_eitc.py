from policyengine_us.model_api import *


class ny_supplemental_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York supplemental EITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (d)(8)
        "https://legislation.nysenate.gov/pdf/bills/2021/S8009C#page=88",
        "https://web.archive.org/web/20221020033542/https://www.tax.ny.gov/pit/child-earned-payments.htm",
    )

    def formula(tax_unit, period, parameters):
        # Tax Law 606(d)(8) pays a share "of the earned income tax credit
        # calculated and allowed pursuant to this subsection", i.e. the
        # New York State EIC of 606(d) after the household credit
        # reduction, not the federal EITC. The 606(d-1)(9) payment on the
        # noncustodial parent (enhanced) EIC is not modeled, as the
        # 606(d-1) credit itself is not modeled. The payment also requires a
        # timely filed return (with extensions); filing dates are not
        # modeled, so that condition is assumed met.
        p = parameters(period).gov.states.ny.tax.income.credits.eitc
        payment = tax_unit("ny_eitc", period) * p.supplemental_match
        # "no payment shall be issued if it is less than twenty-five dollars"
        return where(payment < p.supplemental_minimum_payment, 0, payment)
