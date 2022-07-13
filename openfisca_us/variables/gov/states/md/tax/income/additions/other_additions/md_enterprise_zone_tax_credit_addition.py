## md_enterprise_zone_tax_credit_addition.py
from openfisca_us.model_api import *

class md_enterprise_zone_tax_credit_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Enterprise Zone Tax Credit"
    documentation = (
        "Net additions to income from a trust as reported by the fiduciary"
    )
    unit = USD
    definition_period = YEAR
    # e.Total amount of credit(s) claimed in the current tax year to 6 the extent allowed on Form 500CR for the following Business Tax Credits: Enterprise Zone Tax Credit, Maryland Disability Employment Tax Credit, Small Business Research & Development Tax Credit, Maryland Employer Security Clearance Costs Tax Credit (do not include Small Business First-Year Leasing Costs Tax Credit), and Endowments of Maryland Historically Black Colleges and Universities Tax Credit. In addition, include any amount deducted as a donation to the extent that the amount of the donation is included in an application for the Endow Maryland Tax Credit and/or Endowments of Maryland Historically Black Colleges and Universities Tax Credit on Form 500CR or 502CR.