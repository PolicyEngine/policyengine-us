from policyengine_us.model_api import *


class ct_federal_alternative_minimum_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Adjusted Federal Tentative Minimum Tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-6251_1222.pdf#page=1"  # line 14
        "https://www.irs.gov/pub/irs-pdf/f6251.pdf"
    )

    def formula(tax_unit, period, parameters):
        amt_adjusted = tax_unit("ct_adjusted_amt_income", period)  # Line 5

        filing_status = tax_unit("filing_status", period)
        amt_exemption = parameters(
            period
        ).gov.states.ct.tax.income.alternative_minimum_tax.exemption

        line8 = max(
            amt_adjusted - amt_exemption.initial_exemption[filing_status], 0
        )
        line9 = line8 * amt_exemption.rate
        line10 = max(
            amt_exemption.final_exemption[filing_status] - line9, 0
        )  # Exemption
        line11 = max(amt_adjusted - line10, 0)
        """ line12 = if line 2 and 4 = 0, then line 7 ($1,079,800 if filing jointly or qualifying surviving spouse, 
                                                                              $539,900 if single or head of household, separately);
                                            else if 2 and 4 > 0, then
                                                if file form 2555, then see instructions; 
                                                else complete 6251 part 3 and part2, then enter line 52
                                            else if line 11 (line 1 + line 2 - line 4 (=line 5) - (line 6 - line 9 (=line 10))) is 206,100 (103,050) or less, then line 11 * .26
                                            else line 11 * 0.28 - 4,122 (2,061 if separately)) """
        # line 13 = Alternative minimum tax foreign tax credit from federal Form 6251, Line 8
        # line 14 = line 12 - line 13
        # return line14
