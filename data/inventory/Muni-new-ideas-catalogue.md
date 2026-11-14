# Muni: catalogue of new ideas

All 128 new ideas are below, grouped by theme. Each one has three judge scores: Feasibility (can a credible slice be shown tonight?), Brief fit and Survives scrutiny (the skeptic's score). The headline ranking gives brief fit and scrutiny the most weight.

---

## 1. Headline: the strongest new ideas

1. **The Life of a Decision (N120).** Seven story cards follow one real Dec 8, 2025 item: agenda → staff report → minutes → the Mayor's no-veto decision MD 2025-023 → By-law 2025-087 → later repealed by 2026-047. It turns proposed / decided / in effect into a story. *(F4 · B5 · S4)*
2. **One verification gate (N54, merged with N52, N53, N55 and N81).** The brief's prohibitions run as automated tests, with one failing example shown on camera, plus checks on qualifiers, numbers and decision verbs. It shows "checked against records" happening instead of just claiming it. *(N54: F5 · B5 · S4)*
3. **Windows Wall (N16, with N73 as its data layer).** A deadline gets a clock only when a source states it word for word. "Never infer a deadline" becomes a rule judges can see in the code. *(F5 · B5 · S4)*
4. **The 120-Metre Gap (N37).** Explains why renters (38.7% of Waterloo households) miss statutory notice, and drafts the written notice request that O. Reg. 545/06 s.5(8) allows. *(F3 · B5 · S4)*
5. **Decision Facts panel (N89).** Fixed headings that match the brief's success list, the same for every decision type, and printable. *(F5 · B5 · S3)*
6. **False Friends (N118).** Eight warning chips on trap words ("received for information", "listed", "delegation", "consent"), each tied to a real Waterloo record and measurable in the user test. *(F5 · B4 · S4)*
7. **Heard → Did Register (N71).** Answers the brief's explicit question on showing how public input was considered. It builds on Waterloo's own 2017 comment-tracking table (P214). *(F4 · B5 · S3)*

---

## 2. Justified disagreements with the current plan

Each point gives the disagreement, the reason and the evidence. Points raised by several lenses are merged.

1. **The Calendar tab should list participation windows, not meetings.**
   - *Reason:* a meeting calendar invites the inference the brief forbids (treating a meeting date as a submission deadline).
   - *Evidence:* real deadlines are stated on notices (P209: last day to object Nov 6, 2026; P210: OLT appeal until Nov 8, 2026; P004: committee applications close Nov 17, 2026). Delegation rules are relative to the meeting (P202: register by 10 a.m. Monday; 10 minutes if registered by Friday 10 a.m.). Any window without a published last day should show "not published". Four lenses (staff, governance, analogies, Windows Wall) reached this independently.
2. **Drop the demographic quiz.** Use an on-device ward or stop number for "near me", and ask about preferred formats rather than identity.
   - *Reason:* identity answers don't change what Muni should show, but format needs do, and they carry far less privacy risk.
   - *Evidence:* City Policy A-046 s.1.6 (collect no more than the purpose needs) and s.1.3 (no personal information into AI tools). Ward polygons are already available (P224, 7 features). Matching a GRT stop number to GTFS succeeded for 2,245 of 2,252 stops (N30).
   - Profile answers must never be sent to the LLM as context: different groups would get different framings of the same decision. They must also never be joined to analytics.
3. **Go deep on a few items instead of offering "a consolidated place to review all decisions".**
   - *Reason:* full coverage can't be achieved honestly, and a city will more readily adopt a publishing format and workflow than an outside aggregator.
   - *Evidence:* Region eScribe report PDFs return 403 even in headless Chrome. The P229 dashboard requires a sign-in. City Council Summary posts cite no report numbers (0/4) and link the meeting in only 1 of 4 (P260).
   - Build the demo around one fully documented meeting (Dec 8, 2025: P011, P012, P014, P015, P016, P196, P197, MD 2025-023), one development case (Z-25-23) and OPA 58 as the example of a hand-off between governments. Prefer City items over Region items, and cache dated copies of every cited source. Pitch it as "the explanation layer a city runs on its own records", with a coverage report card (N79) stating the limits.
4. **The Map tab must not present ArcGIS status (P225) as fact.**
   - *Reason and evidence:* L06 found conflicting statuses in 4 of 28 under-review matches and 5 of 52 decided matches, and one address has both an Approved and a Withdrawn row. Each pin needs a status source and a "records disagree" state.
   - P225 timestamps come from a bulk reload (2026-07-06), so they cannot show when anything happened.
5. **Put learning inside the issue pages, not mainly in a separate Learn tab.** If the tab stays, make it an index.
   - *Reason:* retrieval, prediction and contrasting cases beat re-reading explanations. Separate tabs tend to go unvisited, and the brief rewards understanding of real decisions.
   - Teach Waterloo-specific mechanics first, ordered by the costliest misconceptions:
     - consent agendas (P012)
     - strong-mayor no-veto decisions (P008)
     - delegated staff authority (P002)
     - City vs Region
     - provincial approval of OPAs (P264)
     - "listed" vs "designated" heritage (P231)
   - Put the five-step status strip and an inline "we don't know yet" line on every surface, including SMS and print.
   - Make struggle-first exercises optional with a visible "just show me": the cited meta-analysis favoured instruction first for some learners, and struggle hits low-literacy users hardest.
6. **Don't lead the pitch with "AI summaries". Never let an LLM decide status, and avoid an open-ended chatbot.**
   - *Reason:* the team's own research found that no document family needs an LLM at any extraction stage (guide 3.0.6). Status sources parse deterministically: staff-report headers 22/22, the closed vocabulary of minutes dispositions, and mayoral instruments 81/81. A-046 s.1.6 requires that non-AI alternatives be considered.
   - Present AI as a narrow, checked convenience: wording, passage tagging, video alignment.
   - Any question box should answer from records only and refuse in typed categories (N58), because judges will ask "should I oppose this?".
   - Precompute and cache outputs, and allow at most one bounded live call during the demo.
7. **Add a visible staff side.**
   - *Reason:* the brief names clerks, communications and engagement staff, councillors and journalists as users. It asks how a tool could "help municipal staff explain decisions clearly" and how municipalities can "show how public input was considered". It also requires that a municipal leader can use the tool without the team.
   - The current plan is entirely resident-facing. Show at least one end-to-end staff workflow, such as the Heard → Did Register (N71), Enactment Ledger (N69) or Drift Sentinel (N63).
8. **Architecture: one reviewed issue record that feeds every channel.**
   - *Reason:* if web, SMS, voice, print and Easy Read all render the same JSON record, each channel carries the same status, date and source by construction. That also tells a clean software-design story.
   - Phone-first polish matters less than reach. The brief's left-out groups are better served by print, SMS and existing intermediaries.
   - *Caution:* the GRT 57555 text-message habit is not supported by the corpus (0 hits), so don't cite it as fact.
9. **No points, streaks, leaderboards, outcome predictions or vote aggregation.**
   - *Reason:* rewarding "right" answers about contested matters, or forecasting results, breaks neutrality. The critiques of streaks found were blog-level, with no controlled evidence (https://thedecisionlab.com/es-ES/insights/consumer-insights/streak-creep-the-perils-of-too-much-gamification).
   - Score only factual or procedural items. Show recorded votes per item, exactly as the minutes record them.
10. **Don't machine-translate status words, and don't use AI sign-language avatars or voices that sound like the City.**
    - *Reason:* a mistranslated "recommended" or "deferred" breaks the brief's hard constraint. The Region's translation page relies on a Google Translate button.
    - Keep a small reviewed term bank for status words. Use human-recorded audio and ASL, and say plainly where they are missing.
11. **Don't claim that Muni reduces polarisation or "creates informed citizens".**
    - *Reason:* the effect of explanation on attitude extremity (Fernbach) only sometimes replicated. The iCivics and Empaville evidence relies on weak designs or self-report.
    - Claim only gains the team measures itself, for example misread rates or before/after accuracy on four or five items.
12. **Plan for asynchronous judging.**
    - *Evidence:* the FCI page says judging is asynchronous from 10:30. Only the top five pitch live. Videos over three minutes are not considered, and a level-5 video must "distinguish working features from plans". Nothing can be edited after 10 a.m.
    - The video, README and one-page report must carry the score without the team present. A live "break our app" challenge only fits the finals.
    - Never seek or imply a City pilot letter. The honest version is the A-046 crosswalk (N57), which names the City's own required pilot steps.
13. **Don't encode legal rules (appeal standing, statutory timelines) as authoritative app logic.**
    - *Reason:* sources conflict. The skeptic notes that Bill 185 limits official-plan and zoning appeals to specified persons, public bodies and registered owners who made submissions, while third-party appeals of minor variances were removed by Bill 23. The strong-mayor regulation was amended in 2025, and the veto day counts are unverified.
    - Use dates printed on Waterloo's own notices (P208, P209, P210). Label everything else "summary as of [date], verify".
14. **Explain the choice of Waterloo over the brief's Toronto datasets, and show portability.**
    - *Reason:* the brief suggests Toronto's Voting Record and Report Request Log.
    - Port the Request Log idea to Waterloo (N83), or map Decision Cards to Toronto's TMMIS decision statuses (N68), so judges don't read the choice as ignoring the brief.
15. **Council transition (new term starts Nov 15, 2026): show no councillor names or contacts unless verified.**
    - *Evidence:* the ward layer's councillor fields are empty in all 7 wards (P224).
    - A "what the new Council inherits" opening is timely and institutional, but use only the safe variant (N109 B: counts of matters in progress). The legal transition facts and the 2026 mayoral result are unverified.

---

## 3. Full catalogue

**Shared builds (build each once):**
- Dec 8 timestamps: N1, N30, N87
- One deterministic linter: N54, N81, N53, N55
- One quiz and card engine: N19, N20, N21, N22, N23, N36, N98, N118
- One lineage JSON: N85, N120, N80

The pitch and demo ideas (N99–N107) are in section 4.

### 3.1 Meetings, video and proceedings

**N1 · Meeting Rewind.** Each decision gets a "watch it happen" link that opens the City's YouTube council video at that item. The minutes stay the official record.
- **What the user does:** taps "Watch the discussion (starts 1:42:10)". The video opens at that point beside the motion text and result from the minutes. Any transcript excerpt is labelled "machine captions, unofficial".
- **Why it's distinctive:** links video chapters to the formal result in the minutes. The City's video has no chapters (the P016 info.json description is empty). Merged variants: audio-only listening, and a chapter list a clerk can confirm and paste into YouTube.
- **Grounding:** P016 (Dec 8, 2025, YouTube IPFBIBH-OcU, 3 h 18 min, 1,517 timestamped caption lines, items called by number, 19 "carried", one surname spelled three ways), P015, P011, guide 6.4.4 test 11. Precedents: https://councildataproject.github.io, https://citymeetings.nyc. On speech-recognition errors: https://arxiv.org/abs/2402.08021. Word alignment: https://github.com/m-bain/whisperX.
- **Tonight:** hand-align 4–5 Dec 8 items, embed YouTube with `?start=`, copy motion text from P015 (about 1–1.5 h). **Fuller version:** automatic alignment (item-number regex, fuzzy title match, items kept in order) with a clerk confirmation list.
- **Main risk:** not new. eScribe Webcasting Plus, Granicus and CivicPlus already sell item timestamps, and the Region may have them. Never quote or attribute caption text, never index delegates, always link the whole item segment, and pick one variant.
- Feasibility 5 · Brief fit 3 · Survives scrutiny 4

**N5 · Bundled Votes (consent agenda and "report to follow").** Shows which items will pass together in one consent motion and which reports are still marked REPORT TO FOLLOW.
- **What the user does:** sees "Items 4(a)–(d) are approved in one vote unless a member pulls one" and a warning for unpublished reports. After the meeting, sees which items were pulled and their results.
- **Why it's distinctive:** the consent motion decides whether an item gets any discussion, and most residents never see it.
- **Grounding:** P011, P012 (consent range matched 4/4 on Dec 8 and 1/1 on Nov 3; each item keeps its own disposition), P013, P010, L04 (REPORT TO FOLLOW items filled only in the revised packet), P202 for the stated rule.
- **Tonight:** the Dec 8 agenda as cards linked to packet pages (about 2 h). **Fuller version:** live preview from the meeting calendar.
- **Main risk:** residents rarely read upcoming agendas, Councilmatic and eScribe already show consent sections, and P010 has had 403 errors. Simplest form: a "passed in consent motion / pulled" tag. Use neutral wording.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N6 · Receipts for the Council Summary.** Puts the City's or Region's summary post beside everything the minutes record for that meeting.
- **What the user does:** sees two columns, "Highlighted by the City (3)" and "Also decided (11)", or opens a summary item and gets the minutes motion, report number and any by-law.
- **Why it's distinctive:** answers "doesn't the City already do this?" and positions Muni as the bridge between communications text and the clerk's record.
- **Grounding:** P260 (1–4 items per post, 0/4 report numbers, 1/4 meeting links, "Please refer to the minutes for an official record"), P261 (omitted two declarations recorded in P250; N58), P015, L20, worked case 15. Sources: https://www.waterloo.ca/news/posts/city-of-waterloo-council-summary-november-2-2026/ and https://aroundtheregion.ca/making-decisions-that-matter-october-22-edition/.
- **Tonight:** one meeting, hand-built from the minutes (about 1.5 h).
- **Main risk:** the "also decided" list is essentially the minutes' table of contents. It can read as fact-checking the City's communications staff, and Region PDFs return 403. Simplest form: N86 with summary items starred. Never say "omitted".
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N86 · Box Score.** One fixed-column table for every item at a meeting: report number, the exact disposition wording, consent or pulled, recorded counts, by-laws and declared interests.
- **What the user does:** picks "City Council, Dec 8, 2025", scans one table and taps a row to open its explanation. A badge shows when minutes are still a draft.
- **Why it's distinctive:** complete rather than selective, and it teaches meeting structure. No aggregation across meetings and no councillor statistics.
- **Grounding:** P011, P012, P014, P015 (closed vocabulary of dispositions; named opponents on divided votes), L13 (MD 2025-023 approves "all by-laws"; only the minutes give 2025-087 and 2025-088), P260.
- **Tonight:** a Dec 8 table of about 15 rows built by regex and hand-checked, with passage links (about 2 h). **Fuller version:** generated for every meeting.
- **Main risk:** Councilmatic and Legistar already do this, the minutes already are this table, draft minutes change, and vote columns invite scorekeeping.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N87 · Now on the Floor.** A "now serving" page showing which item Council is on and what comes next.
- **What the user does:** sees "Council is live: now on item 6 of 14, your item is 9". The page refreshes itself and needs no account. Afterwards it becomes the item's chapter link.
- **Why it's distinctive:** serves shift workers and delegates who can't wait out a 3-hour meeting. No such indicator was found in P010 or P016. It never predicts times.
- **Grounding:** P202, P203, P011, P012, P016.
- **Tonight:** replay mode on N1's timestamps with a mock "Next item" staff button (1–1.5 h). **Fuller version:** operated by staff during live meetings.
- **Main risk:** needs an operator, eScribe Live already does this where enabled, and a wrong state could make a delegate miss their item. The page must say "The Chair can change the order."
- Feasibility 4 · Brief fit 3 · Survives scrutiny 2

### 3.2 Who decides: authority, tiers and governance rules

**N2 · Mayor's Pen (strong-mayor stage).** Every by-law's timeline shows the Mayor's published decision not to veto it, and its effective date.
- **What the user does:** sees "Council passed (minutes) → Mayor decided not to veto (MD 2025-023, effective Dec 8, 2025) → in effect". A ledger page lists every meeting since July 2023. Oct 6, 2025 shows "not listed; we cannot tell why".
- **Why it's distinctive:** a deterministic, verified series (81/81 instruments parsed) about a step almost nobody knows exists.
- **Grounding:** P007, P008 (81 instruments, 2023-004 to 2026-019, no veto listed), P009, P014, L13, N01, K01, guide 5.5 and 6.4.3. Sources: https://www.waterloo.ca/council-and-committees/mayor-and-city-council/mayoral-decisions/ and https://ontario.ca/document/ontario-municipal-councillors-guide/10-strong-mayor-powers-and-duties. O. Reg. 530/22 (https://www.ontario.ca/laws/regulation/220530): day counts UNVERIFIED.
- **Tonight:** static JSON from K01 as a strip, the Dec 8 chain, and the Oct 6 card (about 2 h). **Fuller version:** joined to every meeting (see N69).
- **Main risk:** veto-window day counts are unverified and the regulation was amended in 2025. A countdown implies drama when there have been 0 vetoes in 81 instruments. The by-law link is class-level by meeting date, and two meetings can share a date. Drop the clock and state the base rate.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 4

**N3 · Signed Off Without a Vote (delegated authority).** Tells residents when a type of matter is approved by staff, so no agenda, debate or minutes will ever exist for it.
- **What the user does:** picks "site plan near me", "a $400k contract" or "Erb Street corridor". The answer cites the schedule row (for example "usually decided by the Director under By-law 2013-124 ss.8–9") and the routes still open to them.
- **Why it's distinctive:** stops residents waiting for a meeting that will never happen. No common civic tool explains delegated authority.
- **Grounding:** P002 (By-law 2025-080, 9 schedules, 78 rows, amended by 2026-018), P039 (Community Planning Permit By-law 2026-034, classes 1–3), P052, P163, P221, K02, L01, N39, guide 5.5. Planning Act s.41(4.0.1) wording UNVERIFIED.
- **Tonight:** 3 hand-checked cards (site plan, contract value band, permit class), each saying "typically, check with the City" (about 2 h). **Fuller version:** a searchable "who can sign X up to $Y" lookup, reviewed by a clerk.
- **Main risk:** a wrong route is worse than none. Value bands overlap, conditions sit in sub-rows, and the online text is an unofficial consolidation. Present delegation as public rules Council set, not as hidden decisions.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 4

**N4 · Who Decides This? (City / Region / Province / tribunal).** Names the body that holds a decision and applies that body's own participation rules.
- **What the user does:** asks about a bus, road, water bill or rezoning. Gets the decider, a source passage and the correct route. City delegation: register by 10 a.m. Monday, 10 or 5 minutes (P202). Region: register by noon a week ahead, 5 minutes, 12 slides maximum (P203). A concern-card variant covers renter issues and cross-tier hand-offs.
- **Why it's distinctive:** comments sent to the wrong government are wasted participation.
- **Grounding:** P202, P203, P216, P237, P238 (117 cells read "Two-tier system"), P239, P243–P246, P264, P265, P266, P106 p.151 (University Ave is a Regional road), P002, P045, P046, P262, N31, N41, N45, guide 5.7. Sources: https://www.regionofwaterloo.ca/business-and-development/growth-and-development-services/regional-official-plan/, https://waterlooregionvotes.org/resources/municipal-structure, https://www.writetothem.com.
- **Tonight:** 5–6 static concern cards (about 2 h). **Fuller version:** about 12 cards with synonym search. Recorded votes appear per item only, never as scorecards.
- **Main risk:** this already exists (the Region's "Who Does What" page, Kitchener's services page, Waterloo Region Votes), and those sources disagree on some services. Simplest form: a "decided by" line plus that body's rules on each issue page.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N13 · Who Left the Room? (closed sessions, declarations, lobbying).** Optional chips for closed-session discussion and written conflict declarations, each with "what this does not establish".
- **What the user does:** on TSD-TRP-26-010, sees declarations in the registry's own wording and a closed-session explainer (s.239 exceptions, Ombudsman route). One variant adds lobbying counts by category.
- **Why it's distinctive:** accountability context that a summary app cannot produce.
- **Grounding:** P250 (87 declarations, 2018–2026), P251, P252 (57 activities, 120 profiles), P253, P255 (Ombudsman since June 1, 2022), P261, P001, N46, N58, L17. Source: https://www.ombudsman.on.ca/en/taxonomy/term/648. City investigator and City registry UNVERIFIED.
- **Tonight:** one Regional item plus an explainer card (about 2 h).
- **Main risk:** the highest defamation and neutrality risk in the set. The data is Region-only, often handwritten scans, and needs name matching. Keep only a generic closed-session explainer, with no per-member chips.
- Feasibility 3 · Brief fit 2 · Survives scrutiny 2

**N109 · Handover: what the new Council inherits.** A dated explainer for the term starting Nov 15, 2026.
- **What the user does:** variant A answers four questions: the restricted period, whether 2023 instruments carry over, who proposes the 2027 budget, and the budget dates. Variant B is an inbox of applications under review, open engagements, plan items in progress and committees recruiting.
- **Why it's distinctive:** a once-in-four-years hook, framed around institutions rather than people.
- **Grounding:** P007, P009 (budget direction covers 2024–2026 only), CORP2023-038, P040 (34 undecided), P004, P198, P075, P016. Sources: https://www.waterloo.ca/council-and-committees/municipal-elections/find-election-candidates/, https://www.waterloo.ca/news/posts/city-of-waterloo-council-summary-june-15-2026/, https://www.amcto.com/node/3899, https://www.wilmot.ca/news/posts/council-restricted-acts-period-in-effect/. UNVERIFIED: whether Waterloo's council was restricted, the 2026 mayoral winner, and the post-election budget rule date (AMCTO and Cochrane disagree).
- **Tonight:** variant B only, as four dated count tiles (1.5–2 h).
- **Main risk:** accuracy of transition law. Say "in progress", not "left open". No councillor rankings.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 2

**N110 · Province Stepped In.** A badge on matters the Province decided, rewrote or made unappealable, plus a dated changelog of provincial bills.
- **What the user does:** sees "Approved by the Province with 14 modifications: the text Council adopted is not the text in force" (OPA 58), or "Minister's Zoning Order: no OLT appeal" (2025 University Ave E).
- **Why it's distinctive:** corrects "Council always has the last word" as a layer across the whole app, not a one-off card.
- **Grounding:** P264, P265, Decision.pdf (14 modifications), K06, K15. Sources: https://www.ontario.ca/laws/regulation/r25012, https://ero.ontario.ca/notice/019-8991, https://www.airdberlis.com/insights/publications/publication/bill-185-cutting-red-tape-to-build-more-homes-act-2024-receives-royal-assent, https://www.ola.org/en/legislative-business/bills/parliament-44/session-1/bill-17.
- **Tonight:** badge two items and a 3–4 row changelog with "verify" flags (about 2 h). **Fuller version:** a six-bill changelog (Bills 3, 23, 109, 185, 200, 17).
- **Main risk:** can read as partisan criticism of the Province, and transition rules are complex. Use flat verbs and verify O. Reg. 12/25 before badging the MZO.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 4

**N113 · Heritage Countdown: Jan 1, 2027.** Listed-but-not-designated heritage properties, and what Ontario law does to them on Jan 1, 2027.
- **What the user does:** sees status chips ("listed, no notice found", "notice issued", "designated, appeal window", "in force") and recent notices. Examples: the notice of intention for 131 William St W (objections until Nov 6, 2026), and five by-laws passed Oct 5, 2026 (2026-079 to 2026-083, e.g. 15 King St N, OLT appeal until Nov 8, 2026).
- **Why it's distinctive:** a live legal deadline backed by real Waterloo notices, and it teaches listed vs designated.
- **Grounding:** P231 (Part IV 42, Part V 137, about 153 listed, a heuristic count per K13), P209, P210, P232, K15. Sources: https://www.airdberlis.com/insights/publications/publication/ontario-extends-the-deadline-for-heritage-property-designation-under-the-ontario-heritage-act, https://www.caledon.ca/en/news/deadline-to-designate-heritage-properties-extended-two-years.aspx. Possible extension to 2030 UNVERIFIED: https://www.countylive.ca/deadline-to-protect-heritage-properties-extended/.
- **Tonight:** a list of about 15 rows, the October notices and one explainer card (2–2.5 h). **Fuller version:** a geocoded map.
- **Main risk:** the deadline can be changed by regulation, so re-verify today. Say "about" for counts, show no owner details, and don't claim the October batch was driven by the deadline.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 4

**N115 · Where Do I Take This? (accountability routes).** Route cards for complaints about how government behaved.
- **What the user does:** picks a situation ("a councillor misused their office", "I want the documents") and sees the tier, what the route can and cannot do, and the stated cost and time. City FOI: $5, generally 45 business days, in person (P256). Region: online form (P257).
- **Why it's distinctive:** gathers statutory routes that are scattered across two governments' sites, and shows the "10 days" vs "10 business days" lobbying discrepancy.
- **Grounding:** P006, P254 (IC2020-01), P255, P256, P257, P252, P253, L18, K16.
- **Tonight:** 5–6 cards (1.5–2 h).
- **Main risk:** outside the brief, may encourage frivolous complaints, and City appointments are unverified. Simplest form: one "raise a concern about process" card.
- Feasibility 4 · Brief fit 2 · Survives scrutiny 3

**N116 · Shot Clock (statutory decision timelines).** How long the City has had an application compared with the provincial decision window.
- **What the user does:** sees the received date, the window and the status, plus an explanation of appeals for non-decision, with a clear "not your deadline" label.
- **Why it's distinctive:** explains timing that residents tend to read as favouritism or stalling.
- **Grounding:** P229 (O. Reg. 73/23 dashboard behind a sign-in), K04 (34 undecided), K13, OLT-22-004241, P205, P206, P011. The 90- and 120-day windows are UNVERIFIED.
- **Tonight:** 2–3 cases, showing "unknown" where dates aren't published (2 h).
- **Main risk:** complete-application dates are usually unpublished and the windows are unverified. Simplest form: a general explainer only.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 2

**N117 · My Two Councils.** An address lookup naming everyone who votes on the resident's issues at both tiers.
- **What the user does:** an on-device lookup shows the ward councillor and Mayor (City), plus Waterloo's Regional councillors, the Mayor and the Regional Chair (Region), each with a "decides on" list.
- **Why it's distinctive:** many residents don't know the Mayor sits on both councils.
- **Grounding:** P224, P227, P251 (16 Regional members), https://waterlooregionvotes.org/resources/municipal-structure.
- **Tonight:** ward lookup plus a static roster flagged "verify after Nov 15" (2 h).
- **Main risk:** the skeptic found the P224 councillor fields empty in all 7 wards, so the original claim is false. Rosters change on Nov 15, and this is already explained elsewhere. Merge into N4.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 2

### 3.3 Decision lifecycle, tracking and record linkage

**N7 · Contract Trail.** Follows a construction project back to its tenders and award amounts, labelling how each link was made.
- **What the user does:** for Albert St, sees design RFP24-07 (May 6, 2024, $136,991.10, 3 bidders), then construction RFT25-01 (Apr 15, 2025, $1,065,260.60, 15 bids, lowest bid won). A flag notes EngageWR still says "Tender approval Fall 2024".
- **Why it's distinctive:** there is no shared project ID, and the award data is hidden in embedded JSON behind "No Awarded Vendors".
- **Grounding:** P215, P216, P219, P220, P188, L16, N39.
- **Tonight:** one trail with explicit vs reconstructed badges (1.5–2 h).
- **Main risk:** only one trail, title-matched links are fragile, bids&tenders is already public, supplier emails must be omitted, and most awards are staff decisions. Off-brief.
- Feasibility 4 · Brief fit 2 · Survives scrutiny 3

**N12 · Approved Is Not Built.** For decided development cases, checks the City's daily building-permit layer.
- **What the user does:** sees "Building permits issued at this address since approval: 0 (as of Nov 13, 2026)" beside EngageWR's own caveat.
- **Why it's distinctive:** closes the gap between decision and construction. P041 carries no construction status.
- **Grounding:** P041 (57 decided), P225, P226 (33,592 permits since 1997, updated daily), guide 5.5.
- **Tonight:** 3 pre-verified, cached addresses (1.5–2 h).
- **Main risk:** address matching is reconstructed, 2,085 permits lack coordinates, and "Complete" is undefined. "0 permits" may be read as stalled, so add an explainer about normal lag. Use only addresses already public as development cases.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N17 · Routine or New?** Labels a staff report as recurring or new using its "Previous Reports on this Topic" chain.
- **What the user does:** sees "Annual item: 4th in a series" on the debt-limit report, with links to CORP2024-046, CORP2023-048 and CORP2022-046, and an optional sparkline (3.37% against a 25% maximum).
- **Why it's distinctive:** helps tell routine statutory items from new policy.
- **Grounding:** P196, P259, N15, N16, N52. Citation errors exist (L10).
- **Tonight:** one report family (1–1.5 h).
- **Main risk:** "routine" may signal "unimportant", and citation typos break chains. Simplest form: an automatic "Previous reports" link list.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N77 · Late-Material Watch.** A feed of what changed between agenda and revised agenda, original and revised packet, and draft and approved minutes.
- **What the user does:** a reporter follows a body and sees, for example, "Dec 8 Revised Packet (47 pp) adds 2 late reports; 2025-086 renumbered 2025-087", or a word-level diff of draft vs approved minutes.
- **Why it's distinctive:** the brief says agendas change, and this spares reporters from re-reading 300-page packets.
- **Grounding:** DF04 §2 and §4 (Dec 8 packet 313 pp, 11 bookmarks; revised packet 47 pp), P014, Oct 6 draft vs final (2 substantive edits; similarity 0.966 not confirmed by the verifier), P010.
- **Tonight:** a static "what changed" page for Dec 8 and Oct 6 (2.5–3 h). **Fuller version:** Atom, RSS or email feed.
- **Main risk:** Councilmatic, eScribe and Granicus already notify on changes. City PDFs have returned 403 and Region PDFs are blocked; don't try to get around the blocking. Timing data must not imply anything was rushed.
- Feasibility 3 · Brief fit 4 · Survives scrutiny 3

**N80 · Item Passport.** One search box that resolves any identifier to the same item and its history.
- **What the user does:** types "Z-25-23", "OPA 58" or "By-law 2025-087" and sees every ID the item has carried, plus a strip showing each stage.
- **Why it's distinctive:** identifiers change between documents, and Waterloo has no item-history page.
- **Grounding:** DF04 §3–4 (DocumentId 13783 → 14449; by-law 2025-086 → 2025-087; agenda section 14 vs minutes section 9; COM vs CAO), P206, P265. Toronto pattern: https://www.toronto.ca/legdocs/mtgmonitor/glossary.htm.
- **Tonight:** hand-made passports for 2–3 items with ID recognisers (2 h).
- **Main risk:** Legistar and Councilmatic use native IDs. Never auto-merge fuzzy matches, Muni's short links must not look official, and the crosswalk needs an owner.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N83 · Report-Back Ledger.** Tracks every Council direction to staff: what was promised, when it is due (if stated), and which later report closed it.
- **What the user does:** sees "Council asked staff to report back on X; no report found yet (as of date)".
- **Why it's distinctive:** brings the brief's own suggested Toronto Report Request Log idea to Waterloo. The "previous reports" chains make closure links plausible.
- **Grounding:** the brief's dataset description, DF04.2 (Section E), DF04.4, DF04 §8 (Dec 8 reserve-fund direction, minutes pp.245–249), P009.
- **Tonight:** 5 hand-found rows from Sep–Dec 2025 minutes and one closure (2–2.5 h).
- **Main risk:** imperfect recall. Use "due date stated", never "overdue", and don't rank departments.
- Feasibility 3 · Brief fit 4 · Survives scrutiny 4

**N84 · Still Good Law?** Legal-citator flags on the plans and by-laws an explanation relies on.
- **What the user does:** sees "Fees By-law 2025-087 [repealed by 2026-047]", "Official Plan consolidation [modified by OPA 58; consolidation doesn't cite it]" or "Uptown Parking Strategy 2008 [no later record found]".
- **Why it's distinctive:** tracks the status of the authorities a decision rests on, not just the decision. Flags come only from explicit wording in records, and the default is grey.
- **Grounding:** P036, P197, L11, P265, P101, P074, P079, P080, P107, P263, DF01 verdict. KeyCite reference: https://www.thomsonreuters.com/en-ca/help/westlaw-edge/tools/keycite/flags-and-icons.html.
- **Tonight:** a table of about 10 rows, flag chips and a history drawer (1.5–2 h).
- **Main risk:** this is legal research, and DF01 says amendment history can't be reconciled from the consolidations. Most flags will be grey, and a false "in effect" flag would do harm.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N85 · Tracking Number.** A package-tracking style event log per matter: who published each event, exceptions, hand-offs between governments, and a staleness clock. Never an ETA.
- **What the user does:** sees entries such as "Dec 16, 2025: hand-off to Province, MMAH approved OPA 58 with 14 modifications" and the banner "Last official record: 47 days ago. No new record does not mean nothing is happening."
- **Why it's distinctive:** hand-offs between governments and a staleness clock, without a progress bar or a "Delivered" state.
- **Grounding:** L04, P012, P015 (Nov 3, 2025 minutes still a draft on Nov 13, 2026), P008, L13, P264–P266, P215.
- **Tonight:** one matter with about 10 events (1.5 h).
- **Main risk:** largely re-presents the earlier status and history ideas, and the clock invites "stalled" readings. Simplest form: exception and hand-off styling on the existing timeline.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 3

**N92 · Where This Rule Came From.** Traces a rule that applies at an address back to the decision that introduced it.
- **What the user does:** sees a site-specific exception "introduced through file Z-xx-xx", an Official Plan section with its OPA 58 change, or "History unavailable".
- **Why it's distinctive:** answers "why does my street allow this?" by working backwards. Credit goes to the deciding body, never to individuals.
- **Grounding:** P037 (Schedule C exceptions C1–C272, 268 IDs, each with a file reference), P038, L11, P231, P210, DF01.
- **Tonight:** 3 Schedule C entries and one Official Plan section (2.5 h).
- **Main risk:** needs legal review, repealed blocks remain in the text, it answers a minority question, and the file-to-page mapping is unverified.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 3

**N95 · Patch Notes.** A monthly changelog of the rules that actually came into effect.
- **What the user does:** reads "Fees: By-law 2026-047 replaces 2025-087; 25 items discontinued" and "Heritage: 15 King St N designated (2026-080)", plus a "what you must now do differently" line.
- **Why it's distinctive:** meets residents after the decision and keeps "decided" separate from "discussed".
- **Grounding:** P036, P197, P210, P265, P008, P262, P231.
- **Tonight:** one month of 6–8 lines (1.5 h).
- **Main risk:** completeness (state which sources are covered), and effect is subtle with staged starts and pending appeals (P210). No winners-and-losers framing.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

### 3.4 Money, budgets and numbers

**N8 · Budget Time Machine.** A capital project's numbers across the tabled, approved and restated budgets, with forecast years shaded "not approved".
- **What the user does:** sees "Tabled $X → Approved $Y → restated $Z" for a project, with its new PROJECT ID.
- **Why it's distinctive:** uses the budget's own ID crosswalk (business-plan reference → REF → PSOFT # → PROJECT ID P01455).
- **Grounding:** P186, P188, P189 (91 files), P192, N19, guide 6.4.4 test 6. The XLSX totals reconcile to p.26.
- **Tonight:** 1 project across 2 versions. **Fuller version:** 3 or more projects across all versions.
- **Main risk:** residents rarely start from a budget code, restatements are partial (6.4.3), and units are in $000s. Simplest form: keep the "forecast, not approved" shading as an N88 rule.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 3

**N9 · Fee Diff.** What City fees changed between by-laws.
- **What the user does:** searches "pool" and sees the old fee (2025-087), the new fee (2026-047), effective dates and DISCONTINUE flags. Report appendices are labelled as proposals.
- **Why it's distinctive:** concrete for renters and families, and it teaches "proposal vs operative".
- **Grounding:** P036 (813 of 1,103 money lines matched; 25 discontinued items), P197, N02, guide 6.4.4 test 2.
- **Tonight:** 8–10 hand-verified rows (2–3 h). **Fuller version:** a full diff.
- **Main risk:** about 26% of lines didn't parse, and a wrong price causes real harm. Show only verified rows and stamp each one "check the by-law".
- Feasibility 3 · Brief fit 3 · Survives scrutiny 4

**N11 · Scorecard with Receipts.** The municipality's self-reported figures shown next to related decisions, dated, with no causal arrows.
- **What the user does:** on a GRT issue, sees ridership of 21.96M (2019), 26.20M (2024) and 22.09M (2025), and bus on-time performance of 74% (2025, 3-minute threshold).
- **Why it's distinctive:** the team rendered a Power BI dashboard that most tools can't read, and checked that monthly figures sum to annual totals for all 8 years.
- **Grounding:** P245, P198 (87 initiatives: 16 complete, 62 on track), P192, P195, P089, L15, L19.
- **Tonight:** a dated snapshot on two issue pages (1 h).
- **Main risk:** placing figures next to decisions invites causal readings, figures change without version history, and the ridership drop is politically loaded. Simplest form: N88 chips, only where a decision cites the figure.
- Feasibility 5 · Brief fit 2 · Survives scrutiny 3

**N88 · What's the 30%? (what a number counts).** Every figure carries a label saying what it measures, its scope, period and status (tabled, approved, forecast) and its data date.
- **What the user does:** taps "7.46%" and reads "Tabled (proposed) 2024 City levy increase; the approved budget shows 6.14%". Taps "74% on time" and reads "GRT bus, 2025, within 3 minutes; the 5-minute threshold gives a different figure."
- **Why it's distinctive:** borrows reference-class discipline from weather forecasting, but never "chance of approval".
- **Grounding:** P204, P187, P245, P195, L14 ($718M vs $777M), P192. Gigerenzer et al. 2005: https://researchonline.lse.ac.uk/id/eprint/16975.
- **Tonight:** a chip component that refuses any number without a status, and 10–15 labelled numbers (1.5 h).
- **Main risk:** labelling takes effort and adds clutter (collapse labels by default). No judgement wording.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 4

**N112 · One Tax Bill, Two Councils / My Tax Receipt.** Shows which council sets each part of a property tax bill. The receipt variant turns the City's own breakdown into a shop-style receipt.
- **What the user does:** in the receipt variant, sees for each $1 of City tax: Fire rescue and enforcement 25¢, capital transfers 21¢, parks and culture 19¢. The 2026 increase of 6.41% (about $107 for the average household) splits into 3.49%, 0.73% and 2.19%. The footer reads "City portion only… confirmed Dec 8, 2025."
- **Why it's distinctive:** comments often go to the wrong budget (for example, transit is Regional).
- **Grounding:** https://www.waterloo.ca/council-and-city-administration/budget-and-financial-reports/budget/property-taxes-and-utility-rates/, https://www.waterloo.ca/news/posts/city-of-waterloo-council-affirms-2026-city-budget/. Also P187 (2024 levy $99,609,666, 6.14%), P189, P193, P196, P197, P009. UNVERIFIED: the City/Region/education shares and the Region's dates. Kitchener's split of about 58/30/12 is not Waterloo's.
- **Tonight:** receipt variant only (1.5 h). **Fuller version:** a two-tier split with both budget calendars.
- **Main risk:** it restates City communications, and how much tax passes to renters is unknown. Never ask for an address or roll number.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

### 3.5 Offline reach, inclusion and accessibility

**N10 · Stop Code Lens / Text the Stop.** Uses the 4-digit EasyGo number on a bus-stop sign as the location.
- **What the user does:** enters stop 1234 and sees the routes serving it, detours that move it, nearby Regional construction and linked transit decisions. An SMS variant takes the code by text.
- **Why it's distinctive:** locates the person without a home address. EasyGo matched GTFS stop codes for 2,245 of 2,252 stops (StopID matched 0). The live alerts feed had 0 entries, so the web posts are the detour source.
- **Grounding:** P244 (46 alerts), P246 (2,265 bus stops, 32 LRT stops), P247, P248 (2,783 rows), P216, P225, P040, N30, N38. Precedent: https://tomarmitage.com/projects/hello-lamp-post.
- **Tonight:** browser lookup of one stop with 1–2 hand-scraped detours (about 3 h in an SMS frame). **Fuller version:** a live number.
- **Main risk:** the GRT 57555 habit is unsupported in the corpus, and it overlaps EasyGo and the Transit app. A radius around a stop is not the notice area (P040: 120 m). It must not look like GRT. Simplest form: the stop number as a "near me" input.
- Feasibility 3 · Brief fit 4 · Survives scrutiny 3

**N37 · The 120-Metre Gap (Renter Relay).** Shows who the law notifies about an application and who it misses, then gives renters a notice request and a printable lobby notice.
- **What the user does:** sees that notice is mailed to owners on the assessment roll within 120 m, and that buildings with 7 or more units are only asked to post it. Taps "I want to be told" to open an email drafting the s.5(8) written request, and can print a dated lobby notice.
- **Why it's distinctive:** answers "why didn't I hear?" by explaining how notice is distributed.
- **Grounding:** P040, P044, P225, P228. O. Reg. 545/06 s.5(4), (5), (7), (7.1), (8), (11): https://www.ontario.ca/laws/regulation/060545. Renters 38.7% (18,205 households) and movers 47.1%: https://www.waterloo.ca/media/3o5lqith/2021-census-profiles-city-of-waterloo.pdf. Print paper closed Sept 2023: https://kitchener.ctvnews.ca/four-local-newspapers-will-no-longer-put-out-print-editions-1.6565524.
- **Tonight:** one application, a "who gets told" card, the email draft and the print notice (about 2 h; 3–4 h with a map). **Fuller version:** every open application.
- **Main risk:** the team's reading of the regulation clauses must be verified, and a buffer drawn around a point is approximate. Never say a person was or wasn't notified, frame it as access rather than mobilisation, show no owner names, and don't paraphrase appeal rights.
- Feasibility 3 · Brief fit 5 · Survives scrutiny 4

**N38 · Text the File Number / Text the Code.** An SMS lookup that answers in three texts, each carrying status, date and source.
- **What the user does:** texts "Z-25-12" and gets "Zoning amendment, staff report not yet tabled (as of [date])". Can reply HOW, SRC or AUDIO.
- **Why it's distinctive:** the 160-character limit forces rigour about status, date and source. It is deterministic, not a chatbot.
- **Grounding:** file-number patterns (guide ~703), P040 (IDs in 26 of 33 titles). Sources: https://grt.ca/rider-information/plan-your-trip/ (57555 unconfirmed), https://www.unicef.org/uganda/what-we-do/u-report, https://tictec.mysociety.org/tainan-city-council-watchbot-empowering-informed-citizens-through-ai/, https://www.twilio.com/docs/messaging.
- **Tonight:** a phone-frame simulator with 3 keywords (1.5–2 h). **Fuller version:** a real number (cost and carrier registration apply).
- **Main risk:** truncation can drop conditions, and file numbers can map to several items. Don't store phone numbers, and start every message with "Muni (not the City)".
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N39 · Dial-a-Decision / Kitchen Table Line.** A phone line with a keypad menu that reads reviewed summaries aloud, with transfers to the City and 211. A variant mails out a fridge sheet.
- **What the user does:** presses their ward number, hears that week's items with the status first, presses 8 for how to have a say, 9 for the City's alternate-format line or 0 for 211.
- **Why it's distinctive:** reaches seniors and residents with low literacy or no internet on a channel they already use.
- **Grounding:** https://www.waterloo.ca/media/ifxocafm/guide-to-ageing-well-in-waterloo-2026-2027.pdf, https://211ontario.ca, City accessibility line 519-747-8780, P034 (A-041: callback within 2 business days), P202, P224/P227, P077, P076, P024. Precedent: GRT phone line 519-585-7555.
- **Tonight:** a keypad simulator with human-read MP3s (about 3 h). Do not route test calls to the City.
- **Main risk:** ongoing cost with no owner, TTS mispronunciation, callers thinking they reached the City, and mail-out addresses needing consent. Keep it as a pilot channel in the readiness report.
- Feasibility 2 · Brief fit 4 · Survives scrutiny 2

**N42 · Connector Kit (for intermediaries).** A facilitator one-pager and a sheet of hard-to-translate terms for settlement workers and library staff.
- **What the user does:** a facilitator prints a 15-minute conversation guide for one issue, with "needs interpreter" flags on tricky terms.
- **Why it's distinctive:** supports the human channel newcomers rely on.
- **Grounding:** https://www.waterloo.ca/news/posts/city-of-waterloo-offers-interpretation-services-in-over-240-languages/ (Voyce interpretation, 7 service points), the Region translation page, https://frontlinetech.km4s.ca/?p=329, P088.
- **Tonight:** one print page and 10–15 terms marked "unreviewed" (2 h).
- **Main risk:** reviewed translations need professionals, agencies are stretched, and partnerships are unverified.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 3

**N43 · Forward-Proof Fact Cards.** Shareable cards with status, an as-of date, the source and a check code that shows whether the card is out of date.
- **What the user does:** shares a card to a group chat. Weeks later, anyone who opens the code sees "Status changed on Dec 1".
- **Why it's distinctive:** designed for forwarding chains that strip out context.
- **Grounding:** https://frontlinetech.km4s.ca/?p=329, and the earlier disagreement-card and as-of history ideas.
- **Tonight:** HTML-to-PNG cards and a /check page (2 h).
- **Main risk:** needs a lasting backend, images can be faked, and forwarding strips alt text. No tracking parameters. Simplest form: an as-of date plus a short link.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N44 · Shelter Bulletins.** Dated bulletins at bus stops near affected sites, keyed to the stop number.
- **What the user does:** reads "Near this stop: proposal for 167–171 King St S. Council has not decided. Valid until [date]."
- **Why it's distinctive:** uses waiting time at stops to reach transit riders.
- **Grounding:** https://grt.ca/rider-information/plan-your-trip/, P246/P249, P243, P245, P040/P225.
- **Tonight:** one A5 bulletin (1–1.5 h).
- **Main risk:** needs Region permission (unverified and unlikely), paper goes stale, placement equity, and it overlaps N122 and N10.
- Feasibility 3 · Brief fit 2 · Survives scrutiny 2

**N45 · Library Desk Mode.** A kiosk mode for library computers: no login, auto-clearing, big type and one-button print.
- **What the user does:** finds their street on a library computer, prints a one-page brief, and the session wipes itself after 3 idle minutes.
- **Why it's distinctive:** handles the privacy problem of shared computers.
- **Grounding:** https://www.wpl.ca/your-library/at-your-library/book-a-computer, hotspot lending (verify), P263.
- **Tonight:** a `?desk=1` flag (1 h).
- **Main risk:** the library's IT and a partnership are unverified, and judges may not notice it.
- Feasibility 5 · Brief fit 3 · Survives scrutiny 3

**N46 · Easy Read Track.** An Easy Read version of each issue with a fixed five-step picture strip for status.
- **What the user does:** chooses "Easy Read" and sees 6–10 short lines with pictures, the current step circled, and a "We do not know yet" line.
- **Why it's distinctive:** Easy Read is a different standard from plain language, and the status strip can be reused on every surface.
- **Grounding:** https://accessible.canada.ca/creating-accessibility-standards/overview-can-asc-31-plain-language-public-review-draft, https://www.inclusioncanada.ca/page/advancing-accessible-communication, https://www.ontario.ca/laws/regulation/110191, P076.
- **Tonight:** one hand-written version, a reusable SVG strip and a toggle (2 h). **Fuller version:** tested with self-advocates.
- **Main risk:** writing it without self-advocates risks tokenism, evidence of benefit is mixed, and pictograms can mislead.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N47 · ASL-First Slots and No-Avatar Policy.** A slot for short ASL videos made by Deaf or certified interpreters, a one-tap request for ASL at the meeting, and a refusal to use AI signing avatars.
- **What the user does:** watches a 60-second ASL summary, or taps "Request ASL for the Dec 1 meeting".
- **Why it's distinctive:** a principled stance (captions are not equivalent for many Deaf people). The City's accessibility page lists no TTY.
- **Grounding:** https://laws-lois.justice.gc.ca/eng/acts/A-0.6/FullText.html (verify s.5.1), the City accessibility page, P034 A-041 s.3.0, Voyce.
- **Tonight:** a slot with an honest "ASL not yet recorded" state and the request composer (1 h).
- **Main risk:** an empty slot looks tokenistic, and the federal act doesn't bind the City. Fold the request into N48.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 2

**N48 · Accommodation Request Composer.** Turns the legal right to accessible formats into a 30-second request about a specific document.
- **What the user does:** taps "I need this in another format" beside a report, picks a format, and gets an email or phone script naming the report number, meeting and page count, addressed to 519-747-8780 or access@waterloo.ca.
- **Why it's distinctive:** few residents know they can request a plain-language version.
- **Grounding:** O. Reg. 191/11 s.12 (https://www.ontario.ca/laws/regulation/110191), the City accessibility page, P076.
- **Tonight:** 1 h.
- **Main risk:** residents may expect Muni to fulfil the request. Say "the City responds; no time is promised". Not legal advice.
- Feasibility 5 · Brief fit 3 · Survives scrutiny 4

**N50 · Ward Radio Minute.** A reviewed two-minute weekly script and podcast feed for community radio.
- **What the user does:** a volunteer host reads that week's script on air.
- **Why it's distinctive:** reaches people with only a radio, and forces status wording to work when spoken.
- **Grounding:** https://radiowaterloo.ca/history/, https://en.wikipedia.org/wiki/CKMS-FM.
- **Tonight:** a script template, an RSS feed and one MP3 (1.5 h).
- **Main risk:** no partnership, weekly review needs staffing, election-period sensitivity. Mention in the readiness report only.
- Feasibility 3 · Brief fit 2 · Survives scrutiny 2

**N51 · Who's Not in the Room.** Places an engagement report's own statements about who responded next to census facts.
- **What the user does:** reads "The report says results are not statistically representative (CORP2024-005) and does not report how many respondents rent. City-wide, 38.7% of households rent."
- **Why it's distinctive:** makes "who is left out" visible using only City documents.
- **Grounding:** P204, P211, P228, the census PDF (renters 38.7%, immigrants 27.5%, movers 47.1%).
- **Tonight:** one card (1–1.5 h).
- **Main risk:** invites conclusions the data can't support. Always say "not reported", never "under-represented". Few reports contain such statements.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N82 · Accessible-Format Desk (staff fulfilment).** Staff produce large print, audio, plain language and braille-ready files from any Muni card, and log requests.
- **What the user does:** a clerk opens a card, picks formats, reviews the output and sends it.
- **Why it's distinctive:** covers the institution's legal duty, not only the resident's reading options.
- **Grounding:** O. Reg. 191/11 s.12, https://accessiblecampus.ca/administrators/iasr/information-communications/section-12/, https://liblouis.io (not fetched), DF03.2, DF04 (born-digital tagged PDFs; P175).
- **Tonight:** an 18-point print PDF, browser speech and a simulated log (1.5 h).
- **Main risk:** human review is required before sending, the requester must be consulted (s.12(2)), and it overlaps N48.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N122 · Lobby Poster (Block Bulletin).** A monthly one-page civic bulletin for apartment lobbies, laundry rooms and library boards.
- **What the user does:** a superintendent, tenant or librarian enters an intersection, prints the poster and posts it.
- **Why it's distinctive:** distributes to a shared physical space rather than an individual subscriber, and collects no data about readers.
- **Grounding:** P040, P044, P262 (Rental Renovation Licensing By-law; $20,000 Tenant Support Fund), P228, P010. Sources: https://www.planningalerts.org.au, https://newpublic.substack.com/p/the-vermont-miracle-how-one-local.
- **Tonight:** a print-ready poster, physically printed (1.5–2 h).
- **Main risk:** posters go stale and landlords may block posting. Print the selection rule and the as-of date. It is close to the earlier printable brief.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N128 · Decision Walk.** A 45-minute self-guided audio walk through Uptown, stopping at real decision sites.
- **What the user does:** hears a 2-minute reviewed clip at each stop (for example, 15 King St N designated by By-law 2026-080).
- **Why it's distinctive:** makes civic understanding physical and social.
- **Grounding:** P210, P209, P233, P219/P220, P042/P070, P090, P108/P179, P140 (27 cultural heritage landscapes).
- **Tonight:** a printed map of 4 stops is the only cheap slice.
- **Main risk:** low reach, high upkeep, contested stops and safety. Treat it as a library or newcomer-program idea.
- Feasibility 2 · Brief fit 2 · Survives scrutiny 2

### 3.6 Participation windows and having a say

**N14 · Already Asked.** Shows the planner Q&A already published for a case before a resident asks.
- **What the user does:** sees "Others asked about: parking (3), height (4), traffic (2)…" with the City's answers.
- **Why it's distinctive:** the Q&A data is hidden behind templates and pagination, and surfacing it reduces duplicate questions for staff.
- **Grounding:** P205 (15 Q&As; `GET {baseUrl}/questions?answered=all&page=N`), N28 (2 of 15 link to PDFs).
- **Tonight:** 1 h.
- **Main risk:** data exists for only one case, moderation hides unpublished questions, and timestamps reflect edits. Strip usernames and never send data to the widget. Simplest form: a section on the Z-25-23 page.
- Feasibility 5 · Brief fit 3 · Survives scrutiny 3

**N15 · Consultation Funnel.** Each consultation shown as counts: notified, attended, comments, responses, changes, and who wrote the summary.
- **What the user does:** sees Water Distribution Master Plan: 5 comments → 5 responses → 0 revisions. Z-25-23: "summary written by the applicant". GRT: "no specific change attributed".
- **Why it's distinctive:** traces the most complete public-input chain in the corpus.
- **Grounding:** P174, P206, P211 Appendix D, P212, P213, P214, L07, L08, N49, guide 5.6.
- **Tonight:** 2–3 cards with aggregate counts only (1.5 h).
- **Main risk:** the only complete chain is from 2017 and contains unredacted personal information (never link P212 or P213). Most stages are blank, and "0 revisions" can read as an accusation. Merge into N71.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 2

**N16 · Open Windows / Windows Wall.** A list of participation windows, each backed by a word-for-word source sentence. No quote, no clock.
- **What the user does:** sees tiles such as "Committee applications close Nov 17, 2026" (with the quote), and "Register to speak: closes 10 a.m. on the Monday of the meeting". Closed windows are greyed with "what you can still do". Conditional states appear ("in force Nov 9 if no appeal"), and rows without a stated date say "closing date not published". Stated dates can be exported to a calendar.
- **Why it's distinctive:** turns the brief's ban on inferred deadlines into a visible rule in the code.
- **Grounding:** P004, P202, P203, P206 (the applicant's deadline, labelled with its issuer), P207, P208, P209, P210, P231, P264–P266, P008, P010, N05, L12. Source: https://www.waterloo.ca/news/posts/city-of-waterloo-council-summary-june-15-2026/.
- **Tonight:** 6–8 tiles, the lint rule and calendar export (2 h). **Fuller version:** N73 as the data layer and N94 as the print and kiosk view.
- **Main risk:** most corpus windows are now closed. Relative rules (P202) need either the rule shown as quoted, or "computed by Muni from the stated rule". Don't mix the Mayor's veto window in with residents' windows, and avoid urgency styling.
- Feasibility 5 · Brief fit 5 · Survives scrutiny 4

**N31 · Five Minutes at the Mic.** Rehearse a Council delegation with the correct time limit.
- **What the user does:** picks an item. The app applies P202 (10 or 5 minutes), offers a structure (who I am, which item, what I'm asking, my evidence) and a countdown timer. Rehearsal stays on the device.
- **Why it's distinctive:** moves from knowing about participation to practising it.
- **Grounding:** P202, P001 ss.12.0 and 25.0, P203. Boal: https://arte-util.org/projects/theatre-of-the-oppressed-legislative-theatre/.
- **Tonight:** 1.5–2 h.
- **Main risk:** P202 cites no by-law, so reconcile it with P001. Never simulate councillors. Simplest form: a static "how to delegate" card with a timer.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N40 · Channel Clock.** The stated rules for each channel (form, email, phone, in person, mail) side by side.
- **What the user does:** sees "Register to speak: form, email or in person (P202)… Phone: callback standard of 2 business days (A-041), so leaving a message is not registering."
- **Why it's distinctive:** exposes channel inequality without computing anything. FOI requests are in person or by mail only (P256).
- **Grounding:** P202, P034, P256 ("electronic submissions will not be accepted"), P001.
- **Tonight:** one delegation table (1.5–2 h).
- **Main risk:** invites date arithmetic, and most cells say "not stated". Simplest form: a "ways to register" row.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N41 · Exposure Preview (Speak Safely).** Before submitting, shows which personal details may become public and what lower-exposure routes exist.
- **What the user does:** drafts a comment. Muni flags addresses and phone numbers and cites P202 ("comments become part of the public record"). It offers alternatives: ask staff a question, use an anonymous survey, or go through a tenant organisation.
- **Why it's distinctive:** protects renters and residents with precarious status, who quietly opt out of participating.
- **Grounding:** P202, P174, P213, P023, P256/P257.
- **Tonight:** a composer with on-device flags; nothing is sent (1.5–2 h).
- **Main risk:** may discourage participation, so the default stays "here's how to submit". Don't point people to the exposed records. The City's current redaction practice is unverified.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 4

**N71 · Heard → Did Register.** Staff log each theme of public input with a standard response code. Muni publishes it beside the decision.
- **What the user does:** staff group comments into themes with counts and pick a code: changed, condition added, out of scope, considered but not adopted (with reason), or under review. Each code links a passage. A resident sees "14 comments about parking → considered, not adopted: report p.12 explains."
- **Why it's distinctive:** answers the brief's explicit question and formalises Waterloo's own 2017 practice.
- **Grounding:** P214 (8 columns: #, From, To, Date Received, Type, Comment, Action, Status), P174, P175, P211. Sources: https://www.calgary.ca/content/dam/www/pda/pd/documents/community-outreach/19-tool-reporttemplate.docx, https://amp.cbc.ca/news/canada/kitchener-waterloo/kitchener-community-engagement-report-1.3931320, https://getinvolved.cityofkingston.ca/why-engage/news_feed/iap2-spectrum-of-public-participation.
- **Tonight:** 4–6 rows for one item and a staff form stored locally (1.5–2 h).
- **Main risk:** overlaps the earlier concern-to-response links. Staff could code everything "considered", so require a passage link per code. Never invent responses for live cases. Themes only, with small groups merged.
- Feasibility 4 · Brief fit 5 · Survives scrutiny 3

**N90 · After-Visit Summary for participants.** A take-home record for a resident who commented or spoke.
- **What the user does:** pastes their comment (stored only on their device) and gets next steps and contacts. Later they see what the record shows, or that it says nothing.
- **Why it's distinctive:** gives participants closure. OpenNotes found larger benefits for patients with less formal education or whose first language isn't English.
- **Grounding:** P202, P214, P174, L07, L08, P205, DF11. Sources: https://www.opennotes.org/news/reading-clinician-visit-notes-can-improve-patients-adherence-to-medications/, https://pmc.ncbi.nlm.nih.gov/articles/PMC3682039.
- **Tonight:** one sample card for Z-25-23 (1.5 h).
- **Main risk:** the follow-up usually finds nothing, since DF11 says attribution of influence is unresolved. Never imply influence.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N94 · Departures Board.** An airport-style board of input windows sorted by closing time, for library screens and lobby posters.
- **What the user does:** glances at the board, scans the "closes" column and scans a QR code. Unverified rows say "Check official page".
- **Why it's distinctive:** a shared screen in a public place, with a fixed status vocabulary.
- **Grounding:** P004, P202, P203, P207, P209 (the objection period must come from the notice itself), P040.
- **Tonight:** a 6-row board, auto-scrolling kiosk mode and an A3 print with QR codes (1.5 h).
- **Main risk:** duplicates N16, the board is nearly empty because most verified windows have closed, and library placement is unverified. No flashing urgency.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 3

**N111 · Can I Still Appeal?** Who has a right to appeal or object, by when (as printed), to which body, and the catch most people miss.
- **What the user does:** sees route cards:
  - Heritage notice of intention: objection to Council by Nov 6, 2026 (P209).
  - Designation by-law: OLT appeal by Nov 8, 2026 (P210).
  - Expropriation: owners have 30 days (P208).
  - Official plan or zoning amendment: most residents can no longer appeal, so speak before Council decides.
  - MZO or provincially approved plan: no appeal.
- **Why it's distinctive:** turns the precondition (having made a submission before the decision) into a "speak now" prompt.
- **Grounding:** P208, P209, P210 (2026-079 to 2026-083), P264, P266, OLT-22-004241, K13. Sources: https://www.airdberlis.com/insights/publications/publication/bill-185-cutting-red-tape-to-build-more-homes-act-2024-receives-royal-assent, https://www.weirfoulds.com/pdf-article?id=36600, https://www.nortonrosefulbright.com/en/knowledge/publications/8e9a48c2/no-appeal-no-problem-abutting-property-owners-without-appeal-rights-may-still-challenge-municipal.
- **Tonight:** 3 cards with printed dates plus the OPA 58 card (1.5 h). Leave out minor variance and zoning standing.
- **Main risk:** close to legal advice. The skeptic notes the removal of minor-variance appeals came from Bill 23, not Bill 185. Tenants usually lack standing, and P209/P210 dates have passed. Simplest form: a general "when you can still have a say" explainer.
- Feasibility 3 · Brief fit 4 · Survives scrutiny 3

**N114 · Four-Test Comment Builder (Committee of Adjustment).** Organises a neighbour's comment around the four statutory tests for a minor variance.
- **What the user does:** answers four prompts (is it minor; is it desirable; does it keep the intent of the Official Plan; does it keep the intent of the zoning by-law). Each links the relevant zoning standard. Dates are copied from the notice.
- **Why it's distinctive:** comments framed around the tests carry weight, and the hearing is often the only venue left.
- **Grounding:** P045 ($1,595 fee rising Sept 1, 2027; date table to Jan 2027), P046, P037, P038. Sources: Planning Act s.45(1) https://www.ontario.ca/laws/statute/90p13, https://www.toronto.ca/wp-content/uploads/2026/09/95ab-committee-of-adjustment-participation-handbook.pdf.
- **Tonight:** a 4-field form on a clearly labelled synthetic example (1.5 h).
- **Main risk:** it is an advocacy aid, so prompts must work equally for supporters and objectors. No live notice is in the corpus. Don't republish applicant names.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N127 · Common Ground (Polis-style).** Residents agree or disagree with neutral statements. Muni shows where groups agree, then hands each person the official route.
- **What the user does:** votes on about 10 statements and sees opinion clusters and statements that bridge them.
- **Why it's distinctive:** surfaces hidden consensus (as in vTaiwan).
- **Grounding:** https://arxiv.org/html/2502.05017v2, https://directory.civictech.guide/listing/polis, P023, P202, P205, P211.
- **Tonight:** not credible; the demo would use synthetic votes only.
- **Main risk:** creates an unofficial consultation people could mistake for the real one, needs moderation, is open to brigading, and is outside "understand decisions". Polis already exists. Roadmap at most.
- Feasibility 2 · Brief fit 2 · Survives scrutiny 1

### 3.7 Staff and institutional tools

**N18 · Publication Health Report.** A periodic audit of where the City's channels disagree, are stale or can't be checked, each with a suggested fix.
- **What the user does:** staff read findings such as "9 cases where GIS and EngageWR disagree", "Z-25-23 summary says 37 storeys; Submission 2 says 30/38", "COM2025-023 vs CAO2025-023", and "10 days vs 10 business days".
- **Why it's distinctive:** turns the team's research into a product a municipal leader can use alone.
- **Grounding:** P225, P040, P041, P014, P229, P253, P256, P202, P001, L06, L10, L21, N13.
- **Tonight:** 6–8 static findings (1–1.5 h), re-verified first.
- **Main risk:** can read as a gotcha, findings may already be fixed, and it overlaps N63, N69 and N79. Merge into N79.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N63 · Drift Sentinel / Paraphrase Drift Checker.** Compares guidance pages with the binding instruments they paraphrase.
- **What the user does:** a resident sees "The Region's page says 10 days; By-law 24-043 s.8.2 says 10 business days. Muni uses the by-law." Staff get a fix list.
- **Why it's distinctive:** catches disagreement between two current documents at different levels of authority.
- **Grounding:** P253 (https://www.regionofwaterloo.ca/government-and-council/transparency-and-accountability/lobbyist-registry/), P256 (45 business days vs MFIPPA s.19), P047, P051, P221 (cites superseded 2019-026 instead of 2025-083), P255, P050, P202 vs P001 s.12.0, P260, P262, DF07 §4 and §8.
- **Tonight:** 3 pre-found cards with both quotes (1 h).
- **Main risk:** deciding which text governs is a legal judgment, so say "differs", not "wrong". False alarms annoy staff. Require exact quotes from both documents.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 4

**N67 · Clerk's Red Pen (staff-report linter).** Structural and plain-language checks built on Waterloo's actual 2025–26 report template.
- **What the user does:** an author pastes a draft and gets a checklist:
  - 7 header labels present
  - sections found by name
  - each recommendation marked as deciding, directing staff or receiving for information
  - placeholders ("[Report Number]", "Choose an item.")
  - narrative figures matching tables (P196)
  - cited previous reports resolve
  - Ward field normalised
  - a 3-sentence resident summary
- **Why it's distinctive:** fixes clarity at the source using the City's own template, not a generic readability score.
- **Grounding:** DF04.2 (header present in 22/22), P118, P147, P196, COM2025-033. Regex `[A-Z]{2,5}\d{4}-\d{3}(\.\d)?`. Sources: https://www.iplfederation.org/iso-standard/, https://www.Vaughan.ca/sites/default/files/CW0203_15_19.pdf, https://dmis.winnipeg.ca/DownloadCouncilPolicyDocument/8569/CO-023.pdf, https://www.planning.org/planning/2017/mar/betterstaffreport.
- **Tonight:** about 6 rules run on 2 Dec 8 reports (2.5–3 h). **Fuller version:** works on any report.
- **Main risk:** an outside tool grading staff is politically sensitive. Keep it private to the author, never suggest changes to substance, and give no single score.
- Feasibility 3 · Brief fit 4 · Survives scrutiny 3

**N68 · Decision Card (open interoperable schema).** Publishes Muni's per-item data model as an open JSON schema mapped to existing civic data standards.
- **What the user does:** a clerk confirms fields for each stage (actor, date, passage), conditions, effective date and the participation window. The card is rendered for residents and published as JSON.
- **Why it's distinctive:** a schema can outlive the hackathon. The pitch to a city becomes "publish this with your agenda", not "buy our app".
- **Grounding:** DF04.4, P008, P265, P210. Sources: https://open-civic-data.readthedocs.io/en/latest/data/vote.html, https://open-civic-data.readthedocs.io/en/latest/data/event.html, https://Schema.org/legislationJurisdiction, https://www.toronto.ca/legdocs/mtgmonitor/glossary.htm.
- **Tonight:** a schema of about 25 fields, 3 cards, a validator, a "View data" button and a mapping table (1.5–2 h).
- **Main risk:** these standards have low adoption in Canada. Call it a "draft profile". Every field needs an evidence pointer, an as-of date and an expiry.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N69 · Enactment Ledger (clerk reconciliation).** Automatically joins minutes, by-law numbers and the Mayor's no-veto decisions, and reports gaps.
- **What the user does:** a clerk sees each meeting's by-laws, whether an instrument exists, the effective date, draft or final status, and anomalies (Oct 6, 2025 has no instrument; COM2025-023 vs CAO2025-023; a "2024 – 0010" typo; 2025-086 → 2025-087). The clerk marks each one explained or corrected.
- **Why it's distinctive:** finds real errors in the official record in seconds and makes "in effect" claims defensible.
- **Grounding:** P008 (81/81, K01), L13, DF03.1 (9 of 11 Sep–Dec 2025 meetings joined), DF04 §6–7, P014, P016 (same-day sessions), P265.
- **Tonight:** a static Sep–Dec 2025 table with 3 anomalies (2–3 h). **Fuller version:** automated.
- **Main risk:** joining by date alone breaks when two meetings share a day, so match on title too. Keep anomalies staff-only. It shows whether records are consistent, not whether something is legally in force.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 4

**N70 · Summary with Receipts / Breadcrumb Check.** Staff draft or lint their Council Summary posts.
- **What the user does:** in the drafting variant, ticks items to highlight and gets a draft with report numbers, minutes links, verb checks and a mandatory "everything else decided" list. In the breadcrumb variant, missing identifiers are flagged with a count of traceable claims.
- **Why it's distinctive:** fits a weekly workflow staff already have.
- **Grounding:** P260 (0/4 report numbers; "40% below its 2010 baseline by 2022" vs "34% reduction from 2010 levels"), P261, P262 ("approved creating" vs "approved the introduction of"), DF04.4, P024 (A-047), P025 (A-046 review), L10.
- **Tonight:** the breadcrumb check on a real P260 post (1.5 h).
- **Main risk:** staff may not adopt an outside critique, and A-046 requires review. Never auto-publish, and pitch it as a time-saver.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N73 · Rulebook Diff.** A maintained table of participation rules with citations and verified-on dates, compared with each item page.
- **What the user does:** for any item, sees the rule, what the item page says, and whether they agree, including "page silent; general rule X; confirm with the Clerk".
- **Why it's distinctive:** makes deadline logic auditable and surfaces inconsistencies between City pages.
- **Grounding:** P202, P203, P004, P206, P207, P208, P209, P210, P001, O. Reg. 545/06. Secondary source (verify): https://blindriver.ca/media/ungl0qdm/zbla-process.pdf.
- **Tonight:** about 10 rules as JSON plus a component (1.5–2 h).
- **Main risk:** goes stale (grey out old rules), P202 doesn't cite P001, and computed dates may look official. Make clear which rights are owner-only. Merge with N16.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 4

**N74 · Notice Companion Kit.** A plain-language companion for each statutory notice, leaving the legal notice untouched.
- **What the user does:** a planner selects P209, reviews the generated companion and exports it for print, SMS (160 characters) and web.
- **Why it's distinctive:** sidesteps legal risk and helps meet AODA s.12(3).
- **Grounding:** P207, P208, P209 (three pages; objection deadline Nov 6, 2026), P210, P229. Sources: https://www.ontario.ca/laws/regulation/110191, https://accessiblecampus.ca/administrators/iasr/information-communications/section-12/.
- **Tonight:** P209 side by side with its companion (2–2.5 h).
- **Main risk:** the corpus notices have expired, the companion could be mistaken for the statutory notice (add a banner), and simplifying heritage text is risky.
- Feasibility 3 · Brief fit 4 · Survives scrutiny 3

**N75 · Neutral Embed.** A locked, always-current Muni card any website can embed with one snippet.
- **What the user does:** a councillor's assistant embeds a card boxed as "non-partisan record (Muni)", with their own commentary outside the box.
- **Why it's distinctive:** carries verified content to places people already read.
- **Grounding:** DF05.2, DF18, P261. Sources: https://www.ctvnews.ca/canada/article/ottawa-commissions-project-to-track-news-deserts-in-canada/; claim unverified: https://www.pressreader.com/canada/the-hamilton-spectator/20210417/281818581661417.
- **Tonight:** an /embed route and a generic mock newsletter (1–1.5 h).
- **Main risk:** sitting next to partisan text can imply endorsement, it needs a hosted backend, there must be no tracking, and it must not use City branding.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N76 · Confusion Radar / Not-a-Submission question box.** Aggregate counts of failed searches and "still unclear" taps for staff, plus an anonymous question box that is clearly not consultation.
- **What the user does:** staff see "41 searches for 'student housing bylaw' returned nothing". A resident asks a question under a "Not a submission" banner.
- **Why it's distinctive:** a continuous signal of what residents don't understand, which can serve as a pilot metric.
- **Grounding:** the brief's Toronto survey finding, DF19, P109, P258, P202. Source: https://en.wikipedia.org/wiki/Pol.is.
- **Tonight:** a question box with seeded, clearly labelled test data (1 h).
- **Main risk:** no real usage data exists, search logs are sensitive, the box could be mistaken for consultation, and it needs moderation. Mention it as a pilot metric only.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 2

**N78 · Pilot-in-a-Box.** A Staff Mode wizard plus a pilot charter, readiness checklist and AI-register entry.
- **What the user does:** a judge pastes a City staff report from 2025–26, confirms each extracted field beside its source passage, previews the card and publishes it locally. They can download a Pilot Charter (Clerk owns records, Communications owns tone, Engagement owns Heard → Did, IT owns hosting; 90-day scope).
- **Why it's distinctive:** literally meets the brief's requirement that a municipal leader can use the tool alone.
- **Grounding:** DF04.2 (22/22), P021, P022. Sources: https://www.waterloo.ca/media/hptgov1j/open-data-policy.pdf, https://ola.org/en/legislative-business/bills/parliament-43/session-1/bill-194, https://www.toronto.ca/city-government/accountability-operations-customer-service/ai-register/, https://www.adelaidemetcalfe.on.ca/sites/default/files/2026-04/IT-1.07%20-%20Use%20of%20AI%20-%20November%203%202025.pdf, https://www.tbs-sct.gc.ca/pol/doc-eng.aspx?id=32592.
- **Tonight:** only the charter and checklist are realistic (about 45 min). The wizard needs 4 hours or more and is fragile.
- **Main risk:** judges will paste unsupported reports (Region 403s, older templates). State which sources are supported, provide manual entry as a fallback, and say "not legal advice".
- Feasibility 2 · Brief fit 5 · Survives scrutiny 3

**N79 · Coverage Report Card and Publisher Fix List.** An honest per-source statement of what is automatic, what needs a person and what is blocked, plus a ranked list of cheap publishing fixes.
- **What the user does:** sees rows such as "City packets: automatic", "P008: automatic, but no by-law numbers", "Region report PDFs: blocked (403)", "bids&tenders: fragile", "Council Summary posts: manual". Fixes include adding report numbers to summaries, listing by-law numbers in instruments, and a stable item ID.
- **Why it's distinctive:** measures coverage instead of asserting it, and hands judges an actionable list.
- **Grounding:** DF04 §4 and §8 (the FileStream 403 also occurs on Kitchener and Guelph hosts), P008, P220, P260, DocumentId drift. Sources: https://www.regionofwaterloo.ca/en/regional-government/open-data.aspx and the City open data policy.
- **Tonight:** 1 h; it doubles as readiness-report content.
- **Main risk:** figures come from samples of 3–5 meetings, so label them. Credit what works, and say nothing about getting around bot protection.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 4

### 3.8 Civic learning games and mechanics

**N19 · Status Sorter.** Residents sort real Waterloo excerpts into piles by who is speaking and with what force.
- **What the user does:** taps 8–10 snippets into piles (staff recommends, committee recommends, Council decided, Mayor's instrument, Province approved, applicant says, City communications) and sees the reason for each.
- **Why it's distinctive:** practises the exact distinction the brief requires, with no AI involved.
- **Grounding:** P013/DF04.2, P015, P008, P260, P262, P206, P264/P265, P019. Roediger & Karpicke 2006; Adesope et al. 2017: https://education.wsu.edu/documents/2018/01/rethinking-use-tests.pdf/. Interleaving effect unverified.
- **Tonight:** 8 excerpts with tap-to-sort (1.5 h).
- **Main risk:** low uptake inside a tab, and borderline labels (P019) could teach the wrong lesson. Link it from issue pages and use 6 staff-verified excerpts.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 4

**N20 · Call It: predict, then reveal.** Predict the outcome of a real past item and rate your confidence, then see the record.
- **What the user does:** predicts and sees reveals such as "OPA 58 approved by the Province with 14 modifications" and "deferred from June 25, then adopted 14 to 1".
- **Why it's distinctive:** surprising reveals help correct exactly the misconceptions the brief worries about.
- **Grounding:** P264/P265 (adopted by By-law 2024-097; approved Dec 16, 2025; in effect Dec 17, 2025; "Appeals are not allowed"), P019, P014, P012, P210. Brod 2021: https://link.springer.com/10.3758/s13423-021-01904-1. Butterfield & Metcalfe: https://dukespace.lib.duke.edu/items/d6ab09ca-f55c-4efb-9d32-2788bc5838b2.
- **Tonight:** 4 cards (1 h).
- **Main risk:** can suggest outcomes are "rigged" or turn into a betting frame. Predict process outcomes only, never councillor votes. Merge into the shared card engine.
- Feasibility 5 · Brief fit 3 · Survives scrutiny 3

**N21 · Twin Cases.** Pairs of real documents that look alike but have different legal force. Spot the differences, then get the principle.
- **What the user does:** compares P209 (notice of intention: opens an objection) with P210 (notice of passing: opens an appeal), and P206 (applicant invitation) with P207 (statutory notice). Also draft vs final minutes, and summary vs minutes.
- **Why it's distinctive:** these are real traps found during parsing, not invented quiz items.
- **Grounding:** P209, P210, P206, P207, P015, P260, P017. Alfieri et al. 2013: https://www.academia.edu/3708913/Learning_through_Case_Comparisons_A_Meta_Analytic_Review.
- **Tonight:** 2 pairs as stacked panels (2 h).
- **Main risk:** hard on a phone. Stamp expired deadlines "past example, do not use" and strip PDF author metadata (P206).
- Feasibility 4 · Brief fit 3 · Survives scrutiny 4

**N22 · Myth Busters.** Fact-first cards that each correct one specific municipal misconception.
- **What the user does:** reads cards such as "The meeting date is not the deadline" (P202, P045), "A Council vote doesn't mean it's in force" (P210, P264/P265), "The summary is not the decision" (P260), "No veto has been listed in 81 instruments" (P008) and "The applicant runs the neighbourhood meeting" (P206).
- **Why it's distinctive:** targets the beliefs that cause missed deadlines.
- **Grounding:** Schroeder & Kucera 2022: https://link.springer.com/article/10.1007/s10648-021-09656-z. Also https://www.osler.com/en/insights/updates/fundamental-changes-made-to-planning-act-appeals-as-bill-185-receives-royal-assent/, the councillor guide and P007.
- **Tonight:** 5 cards (1 h).
- **Main risk:** the skeptic notes that an unqualified "neighbours can't appeal" card would itself be a myth (Bill 185 vs Bill 23 nuance). Limit it to 3–4 myths the corpus proves, with as-of dates.
- Feasibility 5 · Brief fit 3 · Survives scrutiny 3

**N23 · Find the Deadline.** Try the real page first, then see the worked answer and the common wrong answers.
- **What the user does:** answers "When is your last chance to register to speak?" from the source (P202), then sees 3 typical errors and the general rule.
- **Why it's distinctive:** teaches the brief's top safety rule and builds the skill of reading official pages directly.
- **Grounding:** P202, P045, P209, P206, P207. Sinha & Kapur 2021: https://www.x-mol.com/paper/1406031499744456704.
- **Tonight:** 2 challenges with "just tell me" (1.5 h).
- **Main risk:** conflicts with making things easier, and expired dates are a hazard. Make it optional with "just tell me" as the default. Fold into N21 or N19.
- Feasibility 5 · Brief fit 3 · Survives scrutiny 3

**N24 · Spin Doctor (prebunking game).** Players learn distortion techniques by applying them to a real report.
- **What the user does:** applies moves such as status inflation, dropping conditions and confusing deadlines, then sees the passages that expose each one. Output is watermarked.
- **Why it's distinctive:** inoculation games improved detection of misleading headlines.
- **Grounding:** P260, P262, P014, P210, P245. Roozenbeek & van der Linden 2019: https://mediawell.ssrc.org/?p=76433.
- **Tonight:** 2.5 h.
- **Main risk:** produces shareable misinformation about real reports (screenshots defeat watermarks) and frames City communications as spin. Simplest form: a static "common distortions" explainer only.
- Feasibility 3 · Brief fit 2 · Survives scrutiny 2

**N25 · Catch the AI / Spot the Slip.** Residents try to find the error in an AI draft that reviewers caught, then see the correction.
- **What the user does:** taps the wrong sentence in a draft (for example "approved" written for "received for information") and sees the fix.
- **Why it's distinctive:** turns "explain AI's limits" into an experience and builds the habit of checking sources.
- **Grounding:** P001 (a naive regex found 30 of 204 clauses), P209 (a naive regex returns 2024-055), P210, P014, P196, P015, P253. Source: https://arxiv.org/abs/2401.13835.
- **Tonight:** 2–3 exercises built from real catches (1 h).
- **Main risk:** depends on the team actually logging errors (N102). Label any constructed example. Frame it as "how we check".
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N26 · Follow the Item / Choose Your Path (Z-25-23).** Step a real application through its process, choosing at each point what you can do.
- **What the user does:** moves through Submission 1, the applicant's meeting, the Q&A tool and Submissions 2/3. Future stages are greyed out as "not yet in the records".
- **Why it's distinctive:** turns a flowchart into a sequence the player experiences. Endings describe what the process allows, never "winning".
- **Grounding:** P042 (39 items), P206, P205, P070, P044, P202, P266, P264/P265. Sources: Osler (Bill 185), https://www.sciencedaily.com/releases/2014/02/140214130713.htm.
- **Tonight:** a 5–6 node linear stepper (2.5–3 h).
- **Main risk:** Z-25-23 is an active, contested case, and the appeal branch is unverified. Use a completed case, or a "where it is now" stepper without branches.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 3

**N27 · Faded Reading.** Learn to read staff reports through annotated examples, with the annotations gradually removed.
- **What the user does:** reads a fully annotated report, then one with labels hidden, then marks one up alone.
- **Why it's distinctive:** reduces dependence on Muni.
- **Grounding:** DF04.2 reports (P013, P118, P147, P153, P160, P196, P198, P199, P259), P012, P014. Source: https://en.wikipedia.org/wiki/Worked-example_effect.
- **Tonight:** 2–2.5 h.
- **Main risk:** few residents will do it; the real audience is staff training. Simplest form: one annotated "how to read this page" report.
- Feasibility 3 · Brief fit 2 · Survives scrutiny 2

**N28 · Explain It First.** Rate your understanding, try to lay out the causal steps, re-rate, then see the documented chain.
- **What the user does:** orders step tiles for the Rental Renovation Licensing By-law, then sees which steps the record supports and which are "not established".
- **Why it's distinctive:** reveals overconfidence and gives a measure of calibration.
- **Grounding:** P262 ($20,000 Tenant Support Fund; no by-law number or effective date), P260. Fernbach et al. 2013: https://journals.sagepub.com/doi/abs/10.1177/0956797612464058.
- **Tonight:** 1.5 h.
- **Main risk:** mixed replication, can feel patronising, and the reveal is thin. Not worth building now.
- Feasibility 4 · Brief fit 2 · Survives scrutiny 2

**N29 · Source Sleuth.** Lateral-reading drills on real claims.
- **What the user does:** follows the SIFT steps on "OPA 58 is still awaiting approval": project page → ERO (P264) → MMAH notice (P265).
- **Why it's distinctive:** the skill carries over to flyers and group chats that Muni will never cover.
- **Grounding:** P264, P265, P255, P260/P015, P205. Sources: https://ed.stanford.edu/news/it-doesn-t-take-long-learn-how-spot-misinformation-online-stanford-study-finds, https://pressbooks.pub/introtocollegeresearch/chapter/the-sift-method.
- **Tonight:** one drill with cached snapshots (1.5–2 h).
- **Main risk:** curricula already exist, the evidence shows weaker gains for priority groups, and links rot.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N30 · Watch the Vote.** Watch a short clip of a vote, predict what the minutes will record, then compare.
- **What the user does:** answers "who moved it? was it unanimous? was it in the consent motion?" and then sees the P015 entry.
- **Why it's distinctive:** teaches that video records what was said, while minutes record what was decided.
- **Grounding:** P016, P015, P012, P001.
- **Tonight:** one clip with no delegates and 3 questions (1.5 h after the N1 timestamps exist).
- **Main risk:** duplicates N1 and drifts into trivia. Simplest form: a "compare with minutes" panel inside N1.
- Feasibility 4 · Brief fit 2 · Survives scrutiny 3

**N32 · Mock Council Kit.** A printable role-play kit for re-running a real past decision, then comparing with what Council did.
- **What the user does:** a facilitator hands out role cards (Chair, Clerk, staff presenter, delegate, member), a motion sheet and a sealed reveal. Afterwards each participant restates the strongest concern of another group.
- **Why it's distinctive:** reaches classrooms and groups through existing channels.
- **Grounding:** P262, P260, P015, P001, P174/P214, P202, P012, P008, P117/P175/P178. Sources: https://www.dcp.edu.gov.on.ca/en/chv2o-parent-guide, https://studentvote.ca/onmuni/wp-content/uploads/2022/09/Student-Vote-ON-Municipal-2022-Secondary-Lesson-6.pdf, https://eprints.soton.ac.uk/507318, https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/grades/g5-ss, https://schoolweb.tdsb.on.ca/tusc/Grade-5/Our-Local-Government/Curriculum-Links.
- **Tonight:** a one-page printable kit (2 h).
- **Main risk:** sits outside the app, Student Vote already exists, adoption is unverified, and role cards can stereotype. Never assign real councillors as roles. Merge with N49.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 3

**N33 · Who Holds the Pen? (strong-mayor budget game).** A five-turn walk through the strong-mayor budget powers, then a reveal of what Waterloo's Mayor actually did.
- **What the user does:** chooses "who acts next?" at each step, then sees D2023-001 (the Mayor declined to propose the 2024–2026 budget) and 81 no-veto decisions.
- **Why it's distinctive:** grounds a politicised topic in Waterloo's actual, low-drama practice.
- **Grounding:** P007, P008, P009 (Sept 11, 2023; budget per CORP2023-038 not before Feb 2, 2024), P189. Sources: O. Reg. 530/22 and the councillor guide. Council size unverified.
- **Tonight:** 2 h.
- **Main risk:** the 2025 amendments mean hard-coded legal claims may already be stale. Overlaps N2 and N109. Simplest form: one dated explainer card.
- Feasibility 3 · Brief fit 2 · Survives scrutiny 3

**N34 · Same Number, Different Story.** Toggle the definitions behind a real number and predict how it moves.
- **What the user does:** predicts ridership vs boardings, and on-time performance at 3 vs 5 minutes, then answers "What do the records establish about why ridership fell?" (answer: no cause).
- **Why it's distinctive:** teaches people to ask for the definition before accepting a figure.
- **Grounding:** P245, P229, P193.
- **Tonight:** 2 cards (1–1.5 h).
- **Main risk:** GRT is a Regional service and peripheral here. Fold into N88.
- Feasibility 4 · Brief fit 2 · Survives scrutiny 3

**N35 · Brief a Neighbour (checked teach-back).** A resident writes a two-sentence explainer, and Muni checks it before it can be shared.
- **What the user does:** writes about 131 William St W. Checks flag "approved" (the record says "intends to designate"), a missing deadline, or a missing source. The finished card carries the official link.
- **Why it's distinctive:** residents become trusted messengers, with guardrails on accuracy.
- **Grounding:** P209, P210, P202. Fiorella & Mayer unverified.
- **Tonight:** sentence starters and 3 checks (2 h).
- **Main risk:** a "checked" badge gives false assurance, and text can be edited after export. Simplest form: starters that pull status and dates from the record.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 3

**N36 · Recall Before Reveal.** When a followed item changes stage, one optional recall question comes before the update.
- **What the user does:** answers "What needs to happen before this has legal effect?" and then sees the sourced update. Deadlines are always shown first.
- **Why it's distinctive:** the real gaps between stages act as spaced practice.
- **Grounding:** P013 → P019 → P015 → P014 → P210/P265; draft minutes (P015). Roediger; Adesope.
- **Tonight:** 45 min, simulated.
- **Main risk:** needs a follow feature and real stage changes, and the gain is marginal. Skip.
- Feasibility 5 · Brief fit 2 · Survives scrutiny 2

**N49 · Classroom Council (Grade 10 civics kit).** A two-period teacher pack built on one live decision.
- **What the user does:** students fill in a status organiser, write a 100-word explainer checked against Muni's rubric, and take home a family card.
- **Why it's distinctive:** every Ontario student takes CHV2O.
- **Grounding:** https://www.dcp.edu.gov.on.ca/en/chv2o-parent-guide, https://studentvote.ca/onmuni/wp-content/uploads/2022/09/Student-Vote-ON-Municipal-2022-Secondary-Lesson-4.pdf, P003/P004.
- **Tonight:** a lesson plan and worksheet (1–1.5 h).
- **Main risk:** duplicates N32, teacher adoption is unverified, and children shouldn't carry the burden of translating for family. Curriculum codes unverified.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N98 · Say It Back (teach-back with misread rate).** One optional question after each explanation, with anonymous counts of misreadings for staff.
- **What the user does:** picks between "Staff recommend approval; Council has not decided" and "Council approved it", then sees the correction with its passage.
- **Why it's distinctive:** tests the explanation, not the reader, and produces a misread rate per explanation for the user test.
- **Grounding:** P041, P012, P015, P101, P260. AHRQ: https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/teachback.html, https://www.ahrq.gov/evidencenow/tools/health-literacy.html.
- **Tonight:** 2 questions per item and a counter (1 h).
- **Main risk:** small samples, and wrong options could plant misinformation, so show the correct statement prominently. Store nothing per user.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 4

**N118 · False Friends.** Warning chips on municipal words that look familiar but mean something specific.
- **What the user does:** taps "Careful: delegation" and learns it means either a resident speaking to Council (P202) or power handed to staff (P002), and which meaning applies here. Other traps: approved (OPA 58), received for information (P196), listed vs designated (P231), consent (P046), deferred, neighbourhood meeting (P206), and the no-veto label (P008).
- **Why it's distinctive:** narrower and stronger than general definitions, aimed at the words most likely to cause wrong conclusions.
- **Grounding:** corpus cases 7, 8 and 9, P202, P002, P196, P231, P046, P206, K06, P001, P008.
- **Tonight:** 8 chips (1–1.5 h), with an A/B count in the user test.
- **Main risk:** overlaps the earlier inline definitions. A reviewer chooses the meaning in context. Cap at about 8 per screen.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 4

**N123 · Record Detective.** A puzzle game built on real discrepancies in the records, with a flag button for new ones.
- **What the user does:** solves 3-minute cases (the list says "no decision" but the map says "approved"; the by-law cites COM2025-023; "Closed" means engagement closed). Can flag a new one for staff.
- **Why it's distinctive:** teaches critical reading of records and provides free quality checks.
- **Grounding:** P040 vs the layer (of 28 matched, 2 Approved and 2 Appealed active), L10, P041, P225 (bulk reload 2026-07-06), P205, P260.
- **Tonight:** 3 cases and a local flag queue (2–2.5 h).
- **Main risk:** may erode trust and embarrass staff, and cases go stale. Include consistent records too, re-verify each case, and merge with N91.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

### 3.9 Verification, trust and AI safeguards

**N52 · Receipts (claim-level entailment gate).** Each generated sentence must be supported by its cited passage; any that isn't is held back.
- **What the user does:** taps the receipt icon and sees each claim, its passage and a verdict (Supported, Partly, Held back). Staff fix or approve held sentences.
- **Why it's distinctive:** tests support instead of only showing a source. A held-back sentence on screen is visible proof.
- **Grounding:** DF04.2, P196 ("received for information"), guide 3.0.6. AIS: https://arxiv.org/abs/2112.12870. MiniCheck: https://arxiv.org/abs/2404.10774. Citations API: https://docs.claude.com/en/docs/build-with-claude/citations.
- **Tonight:** offline judging for 1–2 issues, cached, with the planted "Council approved a borrowing limit" held back (2.5–3 h).
- **Main risk:** weak on numbers and negation. Label it "supported by cited passage", never "true". Merge into the one gate.
- Feasibility 3 · Brief fit 5 · Survives scrutiny 4

**N53 · Qualifier Keeper.** Flags a summary that drops a condition or hedge present in the source.
- **What the user does:** a "Conditions kept" list shows each qualifier and where it appears. Staff see a "qualifier lost" alert.
- **Why it's distinctive:** catches overstatement that entailment checks miss.
- **Grounding:** P196, P061 Note 9 ("guideline purposes only"), P240 (EES-WAS-26-001), DF04 §8 (REPORT TO FOLLOW, "in principle"), P209. Peters & Chin-Yee: https://arxiv.org/abs/2504.00025.
- **Tonight:** a lexicon of 20–40 patterns with one live catch (1.5 h).
- **Main risk:** misses new hedges and can produce too many flags, so rank by severity.
- Feasibility 4 · Brief fit 5 · Survives scrutiny 4

**N54 · Constraint Linter / Brief Constitution Tests.** The brief's prohibitions written as automated tests that run on every output.
- **What the user does:** presses "Run checks" and sees a test report:
  - REQ-01: sources present
  - REQ-02: status from a fixed list
  - REQ-03: deadlines only from participation or instrument sources, never meeting dates
  - REQ-04: no news summary treated as establishing a decision
  - REQ-05: no emails or phone numbers in quotes

  A deliberately broken example fails on camera.
- **Why it's distinctive:** turns ethics clauses into tests a machine can check, which scores on both the project and software rows.
- **Grounding:** P015 (drafts pre-print "READ AND APPROVED"; Nov 3, 2025 minutes still a draft), P014, P209, P010, P260/K16, P253, taxonomy (guide ~202).
- **Tonight:** 5–6 test rules and one failing example (1–1.5 h).
- **Main risk:** passing tests doesn't mean correct content, and paraphrases ("green light") slip through. Add a synonym list and say so in the README.
- Feasibility 5 · Brief fit 5 · Survives scrutiny 4

**N55 · Number Guard.** The AI never writes numbers. Every figure is inserted from a verified table cell, and conflicts within a source are shown.
- **What the user does:** hovers over "$7.44M" to see the cell and the check behind it, or sees "The report gives two figures".
- **Why it's distinctive:** removes the LLM's weakest area.
- **Grounding:** P196 ($221.01 million in the text vs $221,099,298 in the table; 3.37% vs a 25% maximum; 12/12 column checks), DF12.1, DF04 (COM/CAO).
- **Tonight:** placeholder tokens, a regex for stray digits and the P196 conflict card (1.5–2 h).
- **Main risk:** typos in hand-keyed values (enter them twice) and rounding (use a tolerance). Exclude the P197 fee pages.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 4

**N56 · Glass Box (provenance with an AI-off switch).** Each sentence is marked as a quote, a deterministic extraction, a checked AI paraphrase or human-written. One switch hides every AI sentence.
- **What the user does:** flips "Show without AI" and sees what the AI adds.
- **Why it's distinctive:** makes AI's role inspectable, and matches A-046 s.1.4 (AI must not become a single point of failure).
- **Grounding:** https://www.waterloo.ca/media/qjtorqqp/ai-governance-framework-policy.pdf (P025, s.1.4 and s.1.6), guide 3.0.5.
- **Tonight:** tags, four styles with icons, and the toggle (2 h).
- **Main risk:** colour can't be the only cue (WCAG), and too many styles confuse readers. Default to a calm view.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 4

**N57 · Muni AI Use Record / A-046 Crosswalk.** A plain-language AI disclosure in the format the City's new AI policy requires, mapped clause by clause.
- **What the user does:** a resident reads Tier 1 (what the AI does and never does, personal information: none, how to report an error). Staff read Tier 2 and a 7-row crosswalk covering the PIA, the Security Assessment, subcommittee review, the inventory entry and the non-AI alternative.
- **Why it's distinctive:** ties Muni to a policy approved five months ago, and turns the "pilot next steps" into the City's own procedure.
- **Grounding:** A-046 ss.1.1–1.7, 2.2, 2.5, 3.4 (link above). Sources: https://www.waterloo.ca/news/posts/city-of-waterloo-council-summary-june-8-2026/, https://venturebeat.com/ai/amsterdam-and-helsinki-launch-algorithm-registries-to-bring-transparency-to-public-deployments-of-ai, https://www.gov.uk/government/publications/algorithmic-transparency-template, https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/algorithmic-impact-assessment.html, https://www.ola.org/en/legislative-business/bills/parliament-43/session-1/bill-194, https://www.ontario.ca/laws/statute/s24024.
- **Tonight:** 1 h.
- **Main risk:** A-046 excludes third-party systems that don't use City data. Say "designed to meet if City-hosted", never "compliant". Don't mimic City branding. The policy's procedures are marked TBD.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 4

**N58 · Ask the Record with typed refusals.** A question box that answers only from reviewed records with exact quotes, and otherwise refuses with a stated reason.
- **What the user does:** asks "Is the King St tower approved?" or "Should I oppose it?" and gets a quoted answer or one of six refusals: not in records; records disagree; exists but not public (P229); not decided yet; opinion or advice; already answered by the City (P205).
- **Why it's distinctive:** refusal is a designed output, and the City's own answers are used first.
- **Grounding:** P205, P229, P016, P015. Sources: https://arxiv.org/abs/2407.18418, https://arxiv.org/abs/2509.01476.
- **Tonight:** 6 precomputed questions, rejecting any answer whose quote isn't verbatim (3 h).
- **Main risk:** the most common hackathon entry, live calls can fail, and free text favours confident writers. Lead with the refusal types.
- Feasibility 3 · Brief fit 4 · Survives scrutiny 3

**N59 · Two Readings.** When repeated model answers disagree, Muni shows that the record can be read two ways and quotes the passages behind each.
- **What the user does:** asks about the Dec 8 reserve-fund decision and sees two readings plus "staff have been asked to confirm".
- **Why it's distinctive:** treats disagreement between samples as a signal that the record itself is unclear.
- **Grounding:** Dec 8 minutes pp.245–249 (failed amendment 3–5, then a carried amendment), DF04 §8. Sources: https://arxiv.org/abs/2303.08896, https://www.nature.com/articles/s41586-024-07421-0, https://arxiv.org/abs/2401.13835.
- **Tonight:** 2 cached questions (2 h).
- **Main risk:** mixes model noise with real ambiguity, looks broken to users, and costs more. A human "records unclear" note is better.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 2

**N60 · Devil's Reader.** A second model plays a hurried reader and lists the wrong conclusions such a reader might draw. Each must be prevented by the text.
- **What the user does:** staff see "A reader might conclude the tower is approved: prevented / not prevented".
- **Why it's distinctive:** asks what a reader will believe, not only whether each sentence is true.
- **Grounding:** guide D1 boundary table (~1266), the OPA 58 disagreement, P209.
- **Tonight:** cached, with a before/after on one issue (1–1.5 h).
- **Main risk:** a simulated reader is not evidence about real readers. Use it as an internal pre-screen only, and describe personas by task, not demographics.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N61 · Framing Flip (neutrality audit).** Flags loaded words and compares the summary with supporter and opponent rewrites.
- **What the user does:** staff see flagged words ("much-needed", "massive") and a symmetry check.
- **Why it's distinctive:** tests neutrality instead of asserting it.
- **Grounding:** https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0306621, 446 Albert St (2,823 units), P205, A-046 s.1.5.
- **Tonight:** a loaded-word lexicon on one summary (1.5 h).
- **Main risk:** using an LLM to audit an LLM is circular, a symmetry score is falsely precise, and it risks false balance. Keep only the lexicon inside the linter.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 2

**N62 · Catch Rate Lab.** Plant known errors and publish how many Muni's checks catch.
- **What the user does:** sees "12 planted errors: 10 caught by Receipts; missed: …", and can press "Plant a new error".
- **Why it's distinctive:** shows misses as well as successes, using real error types.
- **Grounding:** P196, COM/CAO, P253 (By-law 24-043 s.8.2), P015, guide 3.0.6.
- **Tonight:** only a tiny version if N54 exists (5 planted errors, raw counts).
- **Main risk:** the gold set is tiny, checks may be tuned to the planted errors, and judges may read the rate as overall accuracy. Combine with N102.
- Feasibility 2 · Brief fit 4 · Survives scrutiny 3

**N64 · Clean Room (privacy scrub and prompt-injection quarantine).** Public correspondence is stripped of personal details and treated strictly as data before any AI reads it.
- **What the user does:** sees themes and counts with "12 personal details removed".
- **Why it's distinctive:** a visible defence where AI could do real harm.
- **Grounding:** P213, P205, DF11, A-046 s.1.3. OWASP: https://genai.owasp.org/llmrisk/llm01-prompt-injection/.
- **Tonight:** scrub a synthetic letter with one planted injection line (2 h).
- **Main risk:** name detection misses handwriting, and the injection demo is somewhat theatrical. Only relevant if correspondence is in scope. Default to themes only.
- Feasibility 3 · Brief fit 4 · Survives scrutiny 4

**N65 · Round-Trip Translation Check.** Translations are translated back and checked for changed meaning. Dates and numbers come from data.
- **What the user does:** sees "Machine-translated; meaning check passed on 14/15 sentences", with the failed sentence shown beside the English.
- **Why it's distinctive:** an honest middle tier until reviewed translation is available.
- **Grounding:** https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/2725080 ("stop" translated as "keep"; errors in 8% of Chinese and 2% of Spanish), https://www.ucsf.edu/news/2019/02/413376/google-translates-doctors-orders-spanish-and-chinese-few-significant-errors.
- **Tonight:** one brief in one language (2 h).
- **Main risk:** matching errors in both directions can cancel out, giving false assurance on deadlines. Keep only "dates from data, English beside deadlines".
- Feasibility 3 · Brief fit 3 · Survives scrutiny 2

**N66 · Plain-Language Ladder with a loss report.** Three reading levels, each held to the same checks, each showing what it leaves out.
- **What the user does:** drags to "Simple" and sees "What this version leaves out: the condition about Ministry approval".
- **Why it's distinctive:** simplifying without quietly dropping conditions.
- **Grounding:** https://arxiv.org/abs/2504.00025, https://www.iso.org/standard/78907.html.
- **Tonight:** 3 levels for one issue (2–2.5 h; needs N53).
- **Main risk:** triples review work, and a long "left out" list defeats the purpose. Use two levels.
- Feasibility 3 · Brief fit 4 · Survives scrutiny 3

**N72 · Redaction Auditor / PII Guard.** Checks documents before publication for personal information and for redactions that don't actually remove the text.
- **What the user does:** a clerk gets a report, by page, of emails, names in bookmarks, and highlight-style "redactions" with text still underneath. It shows counts only, never the hidden text. A variant scrubs everything Muni ingests.
- **Why it's distinctive:** protects residents and the municipality, and meets a hard constraint of the brief.
- **Grounding:** P174 (highlight annotations used as redaction; first names in bookmarks; dark pixels under masks, unconfirmed), P214, P220, P202, P017, P213, A-046 s.1.3. Sources: https://www.ontario.ca/document/freedom-information-and-protection-privacy-manual/chapter-7-privacy-fundamentals; IPC page (unverified) https://www.ipc.on.ca/en/resources/guidance-organizations/guidance-documents-organizations?page=4.
- **Tonight:** run on a synthetic test PDF (2 h).
- **Main risk:** demonstrating it on P174 would point people to a live exposure, so notify the City privately first. The ingestion scrub is the core, and it overlaps N64.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 3

**N81 · Verb & Number Guard / Standard Phraseology.** A closed, published set of decision verbs mapped one-to-one to the wording in the minutes. A checker blocks any upgraded verb.
- **What the user does:** sees the same verbs everywhere, with a plain meaning for each. A draft saying "Council approved" for "received" is blocked.
- **Why it's distinctive:** applies the discipline of aviation radio phrasing to municipal verbs.
- **Grounding:** DF18 (P262 verbs, P260 figures), DF04.4, DF04 §8, P015, P101, P008, P264. Source: https://www.learn-atc.com/wiki/phraseology (secondary).
- **Tonight:** a 15-verb file, a number check and one blocked draft (1–1.5 h).
- **Main risk:** duplicates N53 to N55. Publish the verb glossary for residents.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N91 · Dispute This.** A "this looks wrong" button that routes the problem to the right fixer: Muni misread, the records disagree, or the record itself is wrong.
- **What the user does:** picks a route and pastes a link, sees "Being checked since Nov 14", then the outcome.
- **Why it's distinctive:** separates Muni's errors from the City's, the way credit reports separate the bureau from the source.
- **Grounding:** P040 vs P225 (4 of 28 conflicts), P041, L09, P260, P034. Source: https://www.consumer.equifax.ca/en/personal/education/credit-report/how-to-dispute-credit-report.
- **Tonight:** the button, the form, a banner and one resolved entry (1.5 h).
- **Main risk:** needs moderation, public "under review" banners cast doubt, and it invites brigading. Keep status visible to staff only.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N93 · Behind the Summary (editorial log).** A public log of judgment calls, with the AI draft compared against the published text.
- **What the user does:** taps "How this was written" and sees the diff, 3–5 rationale notes and open questions.
- **Why it's distinctive:** logs why the wording changed, not just what changed.
- **Grounding:** P262, P264 ("fourteen modifications" vs "no modifications were made"), P260. Sources: https://meta.wikimedia.org/wiki/Research:The_role_of_citations_in_how_readers_evaluate_Wikipedia_articles/Trust_taxonomy, https://sri.com/?p=85328.
- **Tonight:** a diff and notes for 1–2 items (1.5 h).
- **Main risk:** a discussion space needs moderation (drop it). Overlaps N102 and N56. Log by role, not by name.
- Feasibility 4 · Brief fit 3 · Survives scrutiny 3

**N108 · Force Ink.** Each sentence is styled by evidentiary force: establishing (the record itself), restated (a paraphrase of a rule) or represented (reported elsewhere).
- **What the user does:** sees solid text for "Council carried motion X (minutes p.4)", a dashed "paraphrase of By-law 24-043" tag, and a hollow "reported, see record" tag.
- **Why it's distinctive:** teaches source-reading by sight.
- **Grounding:** guide ~202, P253, By-law 24-043 s.8.2 (guide lines 444 and 1976), P260.
- **Tonight:** 30–45 min, and it can double as a linter rule.
- **Main risk:** visual noise and a subtle distinction. Use text tags, merge with N56, and log misassigned force as an error type.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 3

### 3.10 Place, visual formats and delight

**N89 · Decision Facts (standard panel).** A panel in the style of a drug-facts label, with the same headings in the same order for every decision type: Applies to, What it would do, Who decides, Conditions, Not decided yet, How to have a say (verified), Records.
- **What the user does:** reads the same layout for a rezoning, a fee by-law or an OPA, and prints it. A banner says "This is not the official notice."
- **Why it's distinctive:** the headings mirror the brief's success list, and the "Applies to" row shows scale (OPA 58 covers all City lands; Z-25-23 is one site).
- **Grounding:** P265, P040, P013, P044, P045. Sources: https://pmc.ncbi.nlm.nih.gov/articles/PMC5779920, https://www.fda.gov/media/150099/download (search summary only).
- **Tonight:** schema, renderer and print view (1.5 h).
- **Main risk:** repackages the earlier status fields, drug-facts labels improved scanning but not recall, and a printout could be mistaken for official. "Not established" must be a valid entry.
- Feasibility 5 · Brief fit 5 · Survives scrutiny 3

**N96 · Term Wrapped (2022–2026 recap).** Shareable, sourced cards recapping what the outgoing Council's instruments did.
- **What the user does:** swipes 8–10 cards (81 no-veto decisions and 0 vetoes, strategic plan counts, ridership) plus a "still pending" card.
- **Why it's distinctive:** a familiar youth format, with selection rules published.
- **Grounding:** P008, P007, P009, P075, P198, P192, P245, P226 (aggregate only), P200. Source: https://amo.on.ca/2026-municipal-elections.
- **Tonight:** 6 cards (2 h).
- **Main risk:** editorial selection right after an election, and ward cards read as scoring councillors. Simplest form: the N109 "in progress" inbox.
- Feasibility 4 · Brief fit 2 · Survives scrutiny 2

**N97 · Segments (route matching).** Draw or pick your usual route and see projects, detours and decisions along it, in route order. The route stays on your device.
- **What the user does:** sees "km 1.2: Moore Ave S reconstruction…; km 3.4: detour…".
- **Why it's distinctive:** matches how people actually move through the city. No sharing and no heatmaps.
- **Grounding:** P215, P216 (57 rows), P217, P244, P246, P248, P225, P224. Source: https://www.npr.org/sections/thetwo-way/2018/01/29/581597949/pentagon-reviews-gps-data-after-soldiers-strava-tracks-are-seemingly-exposed.
- **Tonight:** one preset King St route (3 h).
- **Main risk:** drawing a route is a lot of effort, the Region's text-described limits are hard to geocode, and it excludes people without smartphones. Use "pick a GRT route" instead.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 2

**N106 · Address-Stays-Home ward match.** Answers "is this near me?" by matching the resident's ward on their device, using the report header's "Ward No." field.
- **What the user does:** taps the map, the ward is computed locally, and items for that ward plus city-wide items appear with the note "Ward is an administrative area, not how far effects reach."
- **Why it's distinctive:** the minimum data needed, and a concrete privacy claim ("we cannot see your address").
- **Grounding:** P224 (7 features): https://services.arcgis.com/ZpeBVw5o1kjit7LT/ArcGIS/rest/services/Wards_2026/FeatureServer/0?f=pjson. Report header "Ward No." (guide ~3049), Ward Lookup (P222).
- **Tonight:** map tap, local lookup and filter (1.5–2 h).
- **Main risk:** ward is a poor proxy for proximity, and reports use inconsistent values ("All", "City Wide"). Show adjacent wards, and don't use a geocoder silently.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 3

**N119 · Corner Time Machine.** A slider at one street corner moves from historical air photos to today's rules, the proposal and an "unknown future" frame.
- **What the user does:** scrubs through Past, Built (permit counts per block, never per address), Protected, Rules today, Proposed and Unknown.
- **Why it's distinctive:** ends on uncertainty, which becomes the memorable moment.
- **Grounding:** P226, P231, P209, P210, P072/P073, P037/P038, P225, P040, P042. Source (licensing unverified): https://uwaterloo.ca/library/geospatial/air-photos-digitization-project.
- **Tonight:** not credible beyond placeholders.
- **Main risk:** licensing and georeferencing are unresolved, permits raise privacy issues, and a nostalgic framing reads as anti-development. Simplest form: a three-frame strip (rules today, proposed, unknown).
- Feasibility 2 · Brief fit 3 · Survives scrutiny 2

**N120 · The Life of a Decision (Story Mode).** A swipeable story through one real decision, one document per card.
- **What the user does:** swipes 7 cards:
  1. On the agenda (P011)
  2. Staff recommendation
  3. Council minutes
  4. Mayoral Decision 2025-023 (not vetoed)
  5. By-law 2025-087
  6. Later repealed by 2026-047
  7. The records disagree on a report number

  Each card has a role badge, a date and a source.
- **Why it's distinctive:** makes the strong-mayor step visible and turns "decided" vs "still in force" into a plot. The best 90-second demo moment.
- **Grounding:** the N01 chain, P008 (81 instruments, no veto), P036, L10 (COM2025-023 is a Waterloo Park report; the Sept 22 minutes contain CAO2025-023), renumbering (§7508). O. Reg. 530/22 (day counts unverified).
- **Tonight:** one hard-coded story with buttons and source chips (2.5–3 h).
- **Main risk:** the L10 card must say "appears to cite". Show no veto-window numbers, use calm copy, and provide a linear fallback.
- Feasibility 4 · Brief fit 5 · Survives scrutiny 4

**N121 · Honest Shadows.** Plain grey massing and a sun slider for a proposal, with an "honesty stamp" on every image.
- **What the user does:** uses three tabs: the applicant's own images, a Muni sketch from the stated heights, and what the City's shadow-study terms of reference require.
- **Why it's distinctive:** refuses photoreal renders, and the honesty stamp is part of the visual language.
- **Grounding:** P070 (30/38 storeys), P042, P064 (shadow-study TOR, June 30, 2023), P063 (15/25/40 m). Sources: https://shademap.app/help/, https://github.com/ted-piotrowski/mapbox-gl-shadow-simulator.
- **Tonight:** not credible.
- **Main risk:** Muni's own sketch of an active application persuades and may mislead, and the applicant's study is unverified. Simplest form: link the applicant's study and the P064 checklist only.
- Feasibility 2 · Brief fit 3 · Survives scrutiny 2

**N124 · The "Because" Card.** Start from what you noticed in daily life and trace it to the decision record.
- **What the user does:** picks "Albert Street is closed" and sees work → tender RFT25-01 → budget line → Council meeting, with "record not linked by the City" where the chain breaks.
- **Why it's distinctive:** works backwards from experience, the way residents actually meet decisions.
- **Grounding:** P215, P219, P220, P216, P244, P036, P197, P236 (IPPW2025-046), P188.
- **Tonight:** 2 chains (2 h).
- **Main risk:** causal claims (a detour may be Region or utility work). Use "recorded connection" wording; a fee chain is the safest. Overlaps N7.
- Feasibility 3 · Brief fit 4 · Survives scrutiny 3

**N125 · Civic Weather.** A glanceable widget describing activity in your ward as weather. It never forecasts outcomes.
- **What the user does:** reads "Ward 6 today: Busy. Council meets at 2 p.m. (2 items near you)."
- **Why it's distinctive:** ambient and habitual.
- **Grounding:** P010, P018, P224, P040/P225, P217, P244.
- **Tonight:** a mockup (1.5–2 h).
- **Main risk:** a gimmick that implies forecasts. Ban "storm" language. Not worth building.
- Feasibility 4 · Brief fit 2 · Survives scrutiny 2

**N126 · The Board.** Live applications shown as pieces on a board-game version of the planning process, fading as their evidence ages.
- **What the user does:** taps a piece for its source and date. A piece in two squares means the sources disagree.
- **Why it's distinctive:** makes the age of the data visible.
- **Grounding:** P040, P041, P225, P043–P047, P052, P266.
- **Tonight:** an SVG board (2.5–3 h).
- **Main risk:** the skeptic found that the fading fails, because P225 dates come from a single bulk reload. Mapping statuses to squares is interpretation. Simplest form: a table with "source conflict" rows.
- Feasibility 3 · Brief fit 3 · Survives scrutiny 2

---

## 4. Pitch and demo moves (presentation only)

**N99 · Truth-in-Demo badges.** Every screen element is badged Live, Curated or Planned.
- **Why:** the level-5 demo-video criterion is that it "distinguishes working features from plans", and the badges show the team practises its own honesty.
- **Grounding:** https://fciprojects.ca/hackathons/2026-civic-hack/.
- **Tonight:** a `data-build` attribute and a toggle (30–45 min). Keep the badges on throughout the video.
- **Main risk:** many "Curated" badges can make the app look thin, so explain the choice. The manifest must stay accurate.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 4

**N100 · One-Take Demo under 2:50.** One unedited screen capture of the core workflow, with corrected captions and a 15-second "what's real" table.
- **Plan:**
  - 0:00 problem
  - 0:15 the take
  - 1:50 open the source and show an "unknown" state
  - 2:20 Live / Curated / Planned table
  - 2:40 the ask
- **Grounding:** FCI rules (videos over 3 minutes are not considered; no re-cutting after 10 a.m.). Source: https://cddo.blog.gov.uk/2025/12/04/innovation-in-action-highlights-from-the-local-government-innovation-hackathon/.
- **Main risk:** a bug on camera, so rehearse only Live and Curated paths. Fix caption errors on names.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 4

**N101 · Cost per Verified Brief.** Measured reviewer minutes and model tokens per brief, extrapolated to a meeting cycle.
- **Why:** the report requires a "rough cost", and reviewer time is the number a clerk needs.
- **Grounding:** the FCI report template; P010 and P018 for meeting volume.
- **Tonight:** time each remaining brief (about 30 min of overhead).
- **Main risk:** n = 3, so label it and present a range rather than a quote.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 4

**N102 · Draft-vs-Final AI Error Ledger.** A table of every AI claim the reviewer changed, grouped by which brief constraint it would have violated (status overstated, inferred deadline, dropped condition, wrong passage, personal information).
- **Why:** this is evidence of checking, not an assertion, and it justifies each guardrail.
- **Grounding:** the brief's hard constraints. Contrast: https://opencouncil.network/decisions/184005.
- **Tonight:** a CSV kept during review (30–45 min), with 5 seconds of it in the video.
- **Main risk:** only works if logging starts now. Log zero-error briefs too and never use illustrative counts. Attribute the errors to the AI, not to the City.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 4

**N103 · Living UML and Waterloo-evidence ADRs.** A UML diagram generated from the actual schema, plus 3–4 architecture decision records citing real bottlenecks.
- **Examples:** static reviewed briefs vs live retrieval (P019, P199 and P211 returned 403); status never read from GIS timestamps (P225 has 165 rows with one reload date; 172 vs 165 rows across layers); a licence check at ingestion (162 of 581 entries in P222 have empty licences); a ward filter from the report header (P224 councillor fields empty in all 7 wards).
- **Why:** hits the software rubric ("compare alternatives… concrete scenarios or evidence"; UML that matches the implementation).
- **Grounding:** guide §1.6 (Cloudflare 403s, P229 sign-in, P249 dead DNS).
- **Tonight:** about 1.5 h.
- **Main risk:** don't describe the City as hostile, and never describe getting around bot protection.
- Feasibility 4 · Brief fit 4 · Survives scrutiny 4

**N104 · Second-City Smoke Test.** One brief from another Ontario municipality, plus an "Adapt Muni in 4 steps" box (meeting adapter, ward layer, participation-rule pages, a named reviewer).
- **Grounding:** eScribe hosts in the guide (Region; Guelph). The FCI page asks for "a short case study for other cities".
- **Tonight:** not credible. Include only the 4-step box with a config file.
- **Main risk:** the first thing to cut, some eScribe PDFs are bot-protected, and one example proves little.
- Feasibility 2 · Brief fit 3 · Survives scrutiny 2

**N105 · "Check Us" card and graceful refusal.** A three-step verification challenge at the top of the README for asynchronous judges, plus an "unreviewed item" page that shows the official record and how to have a say, with no AI summary.
- **The hard case:** P210 (15 King St N), which has an appeal deadline of Nov 8, 2026 and shows "in force: not established".
- **Grounding:** the FCI schedule (asynchronous judging 10:30, finalists 12:00), P210 (guide ~1255).
- **Tonight:** 30–45 min.
- **Main risk:** P210's status may have changed since Nov 13. Re-check it this morning or swap it for a stable case.
- Feasibility 5 · Brief fit 4 · Survives scrutiny 3

**N107 · Continuation plan.** An open-source handoff to CivicTechWR, plus a model in which trained, paid residents act as reviewers.
- **Contents:** MIT licence, CONTRIBUTING, 5 good-first issues, and a pilot model in which residents draft and staff sign off.
- **Why:** answers "who maintains this next month?" Nolte et al. found only about 5% of hackathon projects continue past five months.
- **Grounding:** https://par.nsf.gov/biblio/10284449, https://www.meetup.com/CivicTechWR/ (verify on civictechwr.org), https://citybureau.org/notebook/why-ai-will-never-replace-documenters, https://journals.flvc.org/civic/article/view/138710.
- **Tonight:** 30 min.
- **Main risk:** never claim CivicTechWR has agreed ("we will propose"). Paid reviewers need a funder.
- Feasibility 5 · Brief fit 3 · Survives scrutiny 3

---

## 5. Suggested combinations

**A. "Checked against the record": the honesty identity.**
- *Ideas:* N54 one verification gate (absorbing N52, N53, N55, N81), N56 Glass Box with N108 Force Ink tags, N57 AI Use Record and A-046 crosswalk, N102 Error Ledger feeding N25 Catch the AI, N79 Coverage Report Card, N99 Truth-in-Demo badges, N105 Check Us.
- *Why it works:* every piece makes the AI's role and limits visible and testable, which is exactly what the "checked outputs, clear data limits, responsible AI" and software-design rows reward. Most of it is cheap: the linter, badges, crosswalk and ledger together take about 4–5 hours on cached data. It also sets Muni apart from the many "AI summarises council" entries.

**B. "One meeting, end to end": the lifecycle story.**
- *Ideas:* N120 Life of a Decision as the video spine, N86 Box Score for Dec 8, 2025, N1 Meeting Rewind (single hand-checked meeting, with the N30 comparison panel), N2 Mayor's Pen (no countdown) backed by N69 Enactment Ledger, N85 hand-off styling plus N110 badge for OPA 58, N89 Decision Facts panel, N118 False Friends and N98 Say It Back inside the pages, and N88 number labels.
- *Why it works:* the Dec 8, 2025 meeting has the most complete record chain in the corpus (P011, P012, P014, P015, P016, P196, P197, MD 2025-023, By-law 2025-087 → 2026-047). One reviewed lineage JSON drives the story, the box score, the chapters and the panel. It teaches staff vs committee vs council vs Mayor vs Province inside real records rather than in a Learn tab, and gives the strongest storytelling and visualisation moment.

**C. "Have your say, whoever you are": the reach and participation identity.**
- *Ideas:* N16 Windows Wall with N73 as its data layer and N94 as the print/kiosk view, N37 120-Metre Gap, N41 Exposure Preview, N40 "ways to register" row, N48 Accommodation Request Composer, N106 on-device ward match (replacing the quiz), N46 status strip reused on N122 Lobby Poster, N43 forward-proof cards and the N38 SMS simulator, and N71 Heard → Did with N90 After-Visit Summary to close the loop.
- *Why it works:* one reviewed issue record renders to web, print and SMS, so every channel carries the same status, date and source. It answers the brief's "who is left out" (renters 38.7%, offline, low literacy) with cited legal routes (O. Reg. 545/06 s.5(8), O. Reg. 191/11 s.12), enforces the deadline rule visibly, and answers the brief's question on showing how input was considered. It suits the "Most community-centred" award.

---

## 6. Dropped as already covered

None. The list of prior duplicates passed to this round was empty. Ideas that partly overlap the previous model's list are flagged in their entries rather than dropped: N15, N43, N71, N85, N89, N118 and N122.
