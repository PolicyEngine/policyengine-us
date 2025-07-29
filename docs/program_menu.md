# Program Implementation Menu

PolicyEngine can model a wide variety of government benefit and tax programs. This page provides a menu of programs we have implemented or can implement, along with estimated costs for new implementations.

## Available Programs

The table below shows programs by jurisdiction, including implementation status and cost estimates for new implementations.

```{table} Program Implementation Menu
:name: program-menu-table

| Jurisdiction | General Program | Specific Program | Documentation | Estimate ($) | Status | Notes |
|--------------|-----------------|------------------|---------------|--------------|---------|--------|
| **Washington, DC** | | | | | | |
| Washington, DC | TANF | DC TANF + POWER | [Legal Code](https://code.dccouncil.gov/us/dc/council/code/titles/4/chapters/2/subchapters/V) | $2,600 | ✅ Complete | Combination of TANF and supplemental POWER program |
| Washington, DC | SNAP | - | - | $0 | ✅ Complete | Already complete |
| Washington, DC | WIC | - | - | $0 | ✅ Complete | Already complete |
| Washington, DC | General Relief / Assistance | General Assistance for Children program | [Legal Code](https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a?utm_source=chatgpt.com) | $800 | ❌ Not Started | Eligibility based on TANF |
| Washington, DC | Utility Subsidies | DC LIHEAP | [Program Info](https://www.commerce.wa.gov/community-opportunities/liheap/) | $1,400 | ❌ Not Started | [Legal code](https://code.dccouncil.gov/us/dc/council/code/sections/4-261.03) |
| Washington, DC | Child Care Subsidies | DC Childcare subsidy program | [Policy Manual](https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf) | $1,100 | ❌ Not Started | |
| Washington, DC | Medicaid | - | - | $0 | ✅ Complete | Already complete |
| Washington, DC | ACA | - | - | $0 | ✅ Complete | Already complete |
| Washington, DC | Section 8 | | | $800 | ❌ Not Started | |
| Washington, DC | Lifeline | - | - | $0 | ✅ Complete | Already complete |
| **New York, NY** | | | | | | |
| New York, NY | TANF | Temporary Assistance & Family Assistance | [Program Info](https://otda.ny.gov/programs/temporary-assistance/) | $2,200 | ❌ Not Started | |
| New York, NY | SNAP | | | $800 | ❌ Not Started | |
| New York, NY | WIC | - | - | $0 | ✅ Complete | Already complete |
| New York, NY | General Relief / Assistance | NY Cash Assistance | [Program Info](https://www.nyc.gov/site/hra/help/cash-assistance.page) | $1,500 | ❌ Not Started | |
| New York, NY | Utility Subsidies | NY HEAP | [Program Info](https://otda.ny.gov/programs/heap) | $1,100 | ❌ Not Started | |
| New York, NY | Child Care Subsidies | NY CCAP | [Program Info](https://ocfs.ny.gov/programs/childcare/ccap/) | $1,500 | ❌ Not Started | |
| New York, NY | Medicaid | - | - | $0 | ✅ Complete | Already complete |
| New York, NY | ACA | - | - | $0 | ✅ Complete | Not yet complete but funded from MyFriendBen |
| New York, NY | Section 8 | | | $800 | ❌ Not Started | |
| New York, NY | Lifeline | - | - | $0 | ✅ Complete | Already complete |
| **Chicago, IL** | | | | | | |
| Chicago, IL | TANF | IL TANF | [Program Info](https://il.db101.org/il/programs/income_support/tanf/faqs.htm) | $1,300 | ❌ Not Started | [Legal code](https://www.ilga.gov/legislation/ilcs/ilcs4.asp?DocName=030500050HArt%2E+IV&ActID=1413&ChapterID=28&SeqStart=7200000&SeqEnd=11600000) |
| Chicago, IL | SNAP | - | - | $0 | ✅ Complete | Already complete |
| Chicago, IL | WIC | - | - | $0 | ✅ Complete | Already complete |
| Chicago, IL | General Relief / Assistance | - | - | $0 | ✅ Complete | Any specific programs from the Emergency Assistance Fund |
| Chicago, IL | Utility Subsidies | IL LIHEAP | [Program Info](https://dceo.illinois.gov/communityservices/utilitybillassistance/howtoapply.html) | $1,800 | ❌ Not Started | Includes the Utility Billing Relief Program |
| Chicago, IL | Child Care Subsidies | IL CCAP | [Program Info](https://www.dhs.state.il.us/page.aspx?item=9877) | $1,500 | ❌ Not Started | |
| Chicago, IL | Medicaid | - | - | $0 | ✅ Complete | Already complete |
| Chicago, IL | ACA | - | - | $0 | ✅ Complete | Already complete |
| Chicago, IL | Section 8 | | | $800 | ❌ Not Started | |
| Chicago, IL | Lifeline | - | - | $0 | ✅ Complete | Already complete |
| **California Counties** | | | | | | |
| Riverside County, CA | Utility Subsidies | SHARE | [Program Info](https://riversideca.gov/utilities/residents/assistance-programs/share-english) | $2,400 | ✅ Complete | Expedited request |
| Riverside County, CA | General Relief | | | $1,500 | ❌ Not Started | Employment status, loan tracking, dependency on other benefits, county-specific rules |
| Riverside County, CA | Community Action Partnership LIHEAP | | [Program Info](https://capriverside.org/utility-assistance-program) | $600 | ❌ Not Started | 60% SMI test + categorical eligibility requiring SNAP/TANF/SSI checks |
| Alameda County, CA | General Assistance | | [Program Info](https://www.alamedacountysocialservices.org/ex/our-services/Work-and-Money/General-Assistance/index) | $1,800 | ❌ Not Started | Complex time tracking (3 in 12), employability determination, SSI requirements, exemptions |
```

## Total Estimated Cost

**Total for all incomplete programs: $23,300**

## Program Complexity Analysis

When estimating costs for new program implementations, we consider several factors:

### Complexity Factors

1. **Eligibility Rules Complexity**
   - Simple income/asset tests: Low complexity
   - Multiple categorical eligibility paths: Medium complexity
   - Work requirements, time limits, or complex household composition rules: High complexity

2. **Benefit Calculation Complexity**
   - Fixed benefit amounts: Low complexity
   - Income-based sliding scales: Medium complexity
   - Multiple deductions, disregards, or interaction with other programs: High complexity

3. **Geographic Variation**
   - Uniform statewide rules: Low complexity
   - County-level variations: Medium complexity
   - Municipality or district-level rules: High complexity

4. **Data Requirements**
   - Uses existing PolicyEngine variables: Low complexity
   - Requires new data inputs: Medium complexity
   - Requires external data sources or API integrations: High complexity

### Typical Implementation Costs by Program Type

Based on our experience implementing various programs:

- **Basic Cash Assistance Programs (e.g., TANF)**: $1,300 - $2,600
  - Higher costs for programs with work requirements or complex eligibility rules
  
- **Utility Assistance Programs (e.g., LIHEAP)**: $1,100 - $2,400
  - Costs vary based on benefit calculation complexity and geographic variation
  
- **Child Care Subsidies**: $1,100 - $1,500
  - Complex sliding scale calculations and provider payment rates drive costs
  
- **Housing Programs (e.g., Section 8)**: $800+
  - Fair Market Rent calculations and utility allowances add complexity
  
- **Nutrition Programs (e.g., SNAP, WIC)**: $0 - $800
  - Many already implemented; new implementations depend on state-specific rules

### Getting a Custom Quote

For programs not listed above or for more detailed estimates, please contact us. We'll analyze:
- Program regulations and policy manuals
- Existing PolicyEngine infrastructure that can be leveraged
- Required new variables and parameters
- Testing and validation requirements

Contact us at [hello@policyengine.org](mailto:hello@policyengine.org) for a custom implementation quote.