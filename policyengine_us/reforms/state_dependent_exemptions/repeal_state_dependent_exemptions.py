from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_repeal_state_dependent_exemptions() -> Reform:
    class hi_regular_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Hawaii regular exemptions"
        unit = USD
        documentation = (
            "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
        )
        definition_period = YEAR
        defined_for = StateCode.HI

        def formula(tax_unit, period, parameters):
            exemptions_count = tax_unit("head_spouse_count", period)
            p = parameters(period).gov.states.hi.tax.income.exemptions
            # Aged heads and spouses get an extra base exemption.
            person = tax_unit.members
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            aged = person("age", period) >= p.aged_threshold
            aged_head_spouse_count = tax_unit.sum(aged & head_or_spouse)
            total_exemption_count_including_aged = (
                exemptions_count + aged_head_spouse_count
            )
            return total_exemption_count_including_aged * p.base

    class md_total_personal_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "MD total personal exemptions"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MD

        def formula(tax_unit, period, parameters):
            # Get md_personal_exemption from tax_unit multiplied by tax_unit_size
            md_personal_exemption = tax_unit("md_personal_exemption", period)
            tax_unit_size = tax_unit("head_spouse_count", period)
            return md_personal_exemption * tax_unit_size

    class mi_personal_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan personal and stillborn exemptions"
        defined_for = StateCode.MI
        unit = USD
        definition_period = YEAR
        reference = (
            "http://legislature.mi.gov/doc.aspx?mcl-206-30",
            "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf",
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.mi.tax.income.exemptions

            # Personal Exemptions & Stillborn Exemptions
            exemptions = add(
                tax_unit,
                period,
                ["head_spouse_count", "tax_unit_stillborn_children"],
            )
            return exemptions * p.personal

    class ne_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Nebraska exemptions amount"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
            "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
        )
        defined_for = StateCode.NE

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ne.tax.income.exemptions
            return tax_unit("head_spouse_count", period) * p.amount

    class oh_personal_exemptions_eligible_person(Variable):
        value_type = bool
        entity = Person
        label = "Eligible person for the Ohio Exemption Credit"
        definition_period = YEAR
        reference = (
            "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14",
        )
        defined_for = StateCode.OH

        def formula(person, period, parameters):
            # The personal exemption is provided for the head and spouse
            # if they are not claimed as a dependent elsewhere
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            dependent_on_another_return = person(
                "claimed_as_dependent_on_another_return", period
            )
            # The personal exemption is also provided to dependents
            return ~dependent_on_another_return & head_or_spouse

    class ok_count_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Count of Oklahoma exemptions"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
            "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
        )
        defined_for = StateCode.OK

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ok.tax.income.exemptions
            # special exemption AGI eligibility
            fagi = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)
            agi_eligible = fagi <= p.special_agi_limit[filing_status]
            # head exemptions
            age_eligible = (
                tax_unit("age_head", period) >= p.special_age_minimum
            )
            head_exemptions = where(
                tax_unit("blind_head", period), 2, 1
            ) + where(agi_eligible & age_eligible, 1, 0)
            # spouse exemptions
            age_eligible = (
                tax_unit("age_spouse", period) >= p.special_age_minimum
            )
            spouse_exemptions = where(
                filing_status == filing_status.possible_values.JOINT,
                (
                    where(tax_unit("blind_spouse", period), 2, 1)
                    + where(agi_eligible & age_eligible, 1, 0)
                ),
                0,
            )
            # dependent exemptions
            # total number of exemptions
            return head_exemptions + spouse_exemptions

    class ri_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island exemptions"
        unit = USD
        definition_period = YEAR
        reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%20Tax%20Rate%20and%20Worksheets.pdf"
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ri.tax.income.exemption

            exemptions_count = tax_unit("head_spouse_count", period)

            exemption_amount = exemptions_count * p.amount

            # Modified Federal AGI
            mod_agi = tax_unit("ri_agi", period)

            excess_agi = max_(0, mod_agi - p.reduction.start)

            increments = np.ceil(excess_agi / p.reduction.increment)

            reduction_rate = min_(p.reduction.rate * increments, 1)

            return exemption_amount * (1 - reduction_rate)

    class vt_personal_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Vermont personal exemptions"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.VT
        reference = (
            "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf"
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.vt.tax.income.exemption
            is_joint = tax_unit("tax_unit_is_joint", period)
            elsewhere_head = tax_unit("head_is_dependent_elsewhere", period)
            elsewhere_spouse = tax_unit(
                "spouse_is_dependent_elsewhere", period
            )
            eligible_head = (~elsewhere_head).astype(int)
            eligible_spouse = (~elsewhere_spouse).astype(int)
            eligible_count = eligible_head + (eligible_spouse * is_joint)
            # add number of other dependents claimed on federal Form 1040 (line 5c)
            total_exemption_count = eligible_count
            return total_exemption_count * p.personal

    class va_personal_exemption_person(Variable):
        value_type = float
        entity = Person
        label = "Virginia personal exemption for each person"
        defined_for = StateCode.VA
        unit = USD
        definition_period = YEAR
        reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

        def formula(person, period, parameters):
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            amount = parameters(
                period
            ).gov.states.va.tax.income.exemptions.personal
            return amount * head_or_spouse

    class wv_personal_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "West Virginia personal exemption"
        defined_for = StateCode.WV
        unit = USD
        definition_period = YEAR
        reference = "https://code.wvlegislature.gov/11-21/"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.wv.tax.income.exemptions
            tax_unit_size = tax_unit("head_spouse_count", period)
            return where(
                tax_unit_size == 0, p.base_personal, p.personal * tax_unit_size
            )

    class ca_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "CA Exemptions"
        defined_for = StateCode.CA
        unit = USD
        definition_period = YEAR
        reference = "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ca.tax.income.exemptions
            agi = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)
            # calculating phase out amount per credit
            over_agi_threshold = max_(
                0, agi - p.phase_out.start[filing_status]
            )
            increments = np.ceil(
                over_agi_threshold / p.phase_out.increment[filing_status]
            )
            exemption_reduction = increments * p.phase_out.amount
            # Personal Exemptions
            personal_exemption_count = p.personal_scale[filing_status]
            personal_aged_blind_exemption_count = (
                personal_exemption_count + tax_unit("aged_blind_count", period)
            )
            personal_aged_blind_exemption = max_(
                0,
                personal_aged_blind_exemption_count
                * (p.amount - exemption_reduction),
            )
            # Dependent exemptions
            # total exemptions
            return personal_aged_blind_exemption

    class ga_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia Exemptions"
        defined_for = StateCode.GA
        unit = USD
        definition_period = YEAR
        reference = (
            "https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500",
            "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=2c053fd5-32c1-4cc1-86b0-36aaade9da5b&pdistocdocslideraccess=true&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A6348-G0H1-DYB7-W3JT-00008-00&pdcomponentid=234187&pdtocnodeidentifier=ABWAALAADAAL&ecomp=k2vckkk&prid=4862391c-e031-443f-ad52-ae86c6bb5ce2",
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ga.tax.income.exemptions
            filing_status = tax_unit("filing_status", period)

            # Personal Exemptions
            personal_exemptions = p.personal[filing_status]

            # total exemptions
            return personal_exemptions

    class in_base_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Indiana base exemptions"
        unit = USD
        definition_period = YEAR
        reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(3)-(4)
        defined_for = StateCode.IN

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states["in"].tax.income.exemptions
            return tax_unit("head_spouse_count", period) * p.base.amount

    class ia_exemption_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Iowa exemption credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://tax.iowa.gov/sites/default/files/2021-12/IA6251%2841131%29.pdf"
            "https://tax.iowa.gov/sites/default/files/2023-01/IA6251%2841131%29.pdf"
        )
        defined_for = StateCode.IA

        def formula(tax_unit, period, parameters):
            # count adult and dependent exemptions
            adult_count = tax_unit("head_spouse_count", period)
            filing_status = tax_unit("filing_status", period)
            hoh_status = filing_status.possible_values.HEAD_OF_HOUSEHOLD
            hoh_bonus = where(filing_status == hoh_status, 1, 0)
            # count extra adult exemptions based on being elderly and/or blind
            p = parameters(period).gov.states.ia.tax.income
            exemption = p.credits.exemption
            elder_head = tax_unit("age_head", period) >= exemption.elderly_age
            elder_spouse = (
                tax_unit("age_spouse", period) >= exemption.elderly_age
            )
            elder_count = elder_head.astype(int) + elder_spouse.astype(int)
            blind_head = tax_unit("blind_head", period)
            blind_spouse = tax_unit("blind_spouse", period)
            blind_count = blind_head.astype(int) + blind_spouse.astype(int)
            additional_count = elder_count + blind_count
            return (
                (adult_count + hoh_bonus) * exemption.personal
                + additional_count * exemption.additional
            )

    class ks_count_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "number of KS exemptions"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.ksrevenue.gov/pdf/ip21.pdf"
            "https://www.ksrevenue.gov/pdf/ip22.pdf"
        )
        defined_for = StateCode.KS

        def formula(tax_unit, period, parameters):
            filing_status = tax_unit("filing_status", period)
            statuses = filing_status.possible_values
            joint = filing_status == statuses.JOINT
            hoh = filing_status == statuses.HEAD_OF_HOUSEHOLD
            adults = where(joint | hoh, 2, 1)
            return adults

    class ma_income_tax_exemption_threshold(Variable):
        value_type = float
        entity = TaxUnit
        label = "MA income tax exemption threshold"
        unit = USD
        documentation = "MA AGI threshold below which an individual is exempt from State income tax."
        definition_period = YEAR
        reference = "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section5"
        defined_for = StateCode.MA

        def formula(tax_unit, period, parameters):
            filing_status = tax_unit("filing_status", period)
            tax = parameters(period).gov.states.ma.tax.income
            exempt_status = tax.exempt_status.limit
            personal_exemptions_added = (
                exempt_status.personal_exemption_added[filing_status]
                * tax.exemptions.personal[filing_status]
            )
            return (
                exempt_status.base[filing_status] + personal_exemptions_added
            )

    # Using head and spouse count instead of exemptions count
    class wi_base_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Wisconsin base exemption"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf"
            "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf"
            "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf"
            "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf"
            "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
        )
        defined_for = StateCode.WI

        def formula(tax_unit, period, parameters):
            # compute base exemption amount
            p = parameters(period).gov.states.wi.tax.income
            return tax_unit("head_spouse_count", period) * p.exemption.base

    class de_personal_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Delaware personal credit"
        unit = USD
        definition_period = YEAR
        reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf"
        defined_for = StateCode.DE

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.de.tax.income.credits
            head_spouse_count = tax_unit("head_spouse_count", period)
            return p.personal_credits.personal * head_spouse_count

    class ky_family_size_tax_credit_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "Kentucky family size tax credit rate"
        unit = "/1"
        definition_period = YEAR
        reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188"
        defined_for = StateCode.KY

        def formula(tax_unit, period, parameters):
            income = tax_unit("ky_modified_agi", period)
            fpg = parameters(period).gov.hhs.fpg
            # This will be CONTIGUOUS_US for Kentucky.
            state_group = tax_unit.household("state_group", period)
            p1 = fpg.first_person[state_group]
            padd = fpg.additional_person[state_group]
            family_size = tax_unit("head_spouse_count", period)
            # No more than 4 people are accounted for in the credit
            p = parameters(period).gov.states.ky.tax.income.credits.family_size
            capped_family_size = min_(family_size, p.family_size_cap)
            poverty_index = p1 + padd * (capped_family_size - 1)
            share = income / poverty_index
            return p.rate.calc(share, right=True)

    class ok_child_care_child_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Oklahoma Child Care/Child Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
            "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
        )
        defined_for = StateCode.OK

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ok.tax.income.credits
            # determine AGI eligibility
            us_agi = tax_unit("adjusted_gross_income", period)
            agi_eligible = us_agi <= p.child.agi_limit
            # determine OK cdcc amount
            us_cdcc = tax_unit("cdcc", period)
            ok_cdcc = us_cdcc * p.child.cdcc_fraction
            # determine prorated fraction
            ok_agi = tax_unit("ok_agi", period)
            # Compute OK AGI as a share of US AGI.
            # Use a mask rather than where to avoid a divide-by-zero warning.
            agi_ratio = np.zeros_like(us_agi)
            mask = us_agi != 0
            agi_ratio[mask] = ok_agi[mask] / us_agi[mask]
            prorate = min_(1, max_(0, agi_ratio))
            # receive greater of OK cdcc or OK ctc amounts prorated if AGI eligible
            return agi_eligible * prorate * ok_cdcc

    class reform(Reform):
        def apply(self):
            self.neutralize_variable("al_dependent_exemption")
            self.neutralize_variable("il_dependent_exemption")
            self.neutralize_variable("la_dependents_exemption")
            self.neutralize_variable("mn_exemptions")
            self.neutralize_variable("ms_dependents_exemption")
            self.neutralize_variable("nj_dependents_exemption")
            self.neutralize_variable("ny_exemptions")
            self.neutralize_variable("sc_dependent_exemption")
            self.neutralize_variable("ut_personal_exemption")
            self.neutralize_variable("nc_child_deduction")
            self.neutralize_variable("nm_deduction_for_certain_dependents")
            self.neutralize_variable("mt_dependent_exemptions_person")
            self.neutralize_variable("az_dependent_tax_credit")
            self.neutralize_variable("ar_personal_credit_dependent")
            self.neutralize_variable("id_ctc")
            self.neutralize_variable("me_dependent_exemption_credit")
            self.update_variable(hi_regular_exemptions)
            self.update_variable(md_total_personal_exemptions)
            self.update_variable(mi_personal_exemptions)
            self.update_variable(ne_exemptions)
            self.update_variable(oh_personal_exemptions_eligible_person)
            self.update_variable(ok_count_exemptions)
            self.update_variable(ri_exemptions)
            self.update_variable(vt_personal_exemptions)
            self.update_variable(va_personal_exemption_person)
            self.update_variable(wv_personal_exemption)
            self.update_variable(ca_exemptions)
            self.update_variable(ga_exemptions)
            self.update_variable(in_base_exemptions)
            self.update_variable(ks_count_exemptions)
            self.update_variable(ma_income_tax_exemption_threshold)
            self.update_variable(wi_base_exemption)
            self.update_variable(ia_exemption_credit)
            self.update_variable(de_personal_credit)
            self.update_variable(ky_family_size_tax_credit_rate)
            self.update_variable(ok_child_care_child_tax_credit)

    return reform


def create_repeal_state_dependent_exemptions_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_repeal_state_dependent_exemptions()

    p = parameters.gov.contrib.repeal_state_dependent_exemptions

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_repeal_state_dependent_exemptions()
    else:
        return None


repeal_state_dependent_exemptions = (
    create_repeal_state_dependent_exemptions_reform(None, None, bypass=True)
)
