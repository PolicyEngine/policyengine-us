from policyengine_us.model_api import *


class nc_mortgage_and_property_tax_limitation(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina mortgage interest and real estate property tax limitation"
    unit = USD
    definition_period = YEAR
    documentation = "Form D-400 Schedule A line 4: $20,000 per return, shared by spouses filing separate returns. When the spouses' combined amounts before limitation exceed $20,000, each spouse's limitation is their prorated share of $20,000."
    reference = (
        # N.C. Gen. Stat. 105-153.5(a)(2)b
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        # 2025 Form D-401 instructions, Form D-400 Schedule A line 4
        "https://www.ncdor.gov/2025-d-401-individual-income-tax-instructions/open#page=20",
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        cap = parameters(
            period
        ).gov.states.nc.tax.income.deductions.itemized.cap.mortgage_and_property_tax
        person = tax_unit.members
        # "For spouses filing as married filing separately or married filing
        # jointly, the total mortgage interest and real estate taxes claimed by
        # both spouses combined may not exceed $20,000." A joint return holds
        # both spouses, so the cap applies to it once. A spouse filing
        # separately is in another tax unit. Reach them through the marital
        # unit only when it holds exactly two people who each head a separate
        # return: without explicit marital units, everyone shares one default
        # unit.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        head = person("is_tax_unit_head", period)
        separate_head = head & tax_unit.project(separate)
        couple = (person.marital_unit.nb_persons() == 2) & (
            person.marital_unit.sum(separate_head) == 2
        )
        # Each spouse's amount before limitation (Schedule A line 3), on the
        # head of their own return.
        before_limitation = tax_unit(
            "nc_mortgage_and_property_tax_before_limitation", period
        )
        own = head * tax_unit.project(before_limitation)
        combined = person.marital_unit.sum(own)
        # "If the amount of the mortgage interest and real estate taxes paid by
        # both spouses exceeds $20,000, these deductions must be prorated based
        # on the percentage paid by each spouse."
        paid_share = np.divide(
            own, combined, out=np.zeros_like(own), where=combined > 0
        )
        # "For joint obligations paid from joint accounts, the proration is
        # based on the income reported by each spouse for that taxable year."
        # Income is federal adjusted gross income (Form D-400 line 6), not
        # below zero; the shares are equal when neither spouse has any.
        agi = max_(tax_unit("adjusted_gross_income", period), 0)
        own_income = head * tax_unit.project(agi)
        combined_income = person.marital_unit.sum(own_income)
        income_share = where(
            combined_income > 0,
            np.divide(
                own_income,
                combined_income,
                out=np.zeros_like(own_income),
                where=combined_income > 0,
            ),
            0.5,
        )
        joint_account = person.marital_unit(
            "mortgage_and_real_estate_taxes_paid_from_joint_account", period
        )
        share = where(joint_account, income_share, paid_share)
        prorated = head & couple & (combined > cap)
        return where(
            tax_unit.any(prorated),
            cap * tax_unit.sum(where(prorated, share, 0)),
            cap,
        )
