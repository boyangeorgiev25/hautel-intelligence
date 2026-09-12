# WP2 golden-set run — 2026-09-12 11:20

Model: claude-opus-5. Cases: 20 (19 scored + 1 rollback).

## Summary

| | Keyword baseline | AI engine |
|---|---|---|
| Correct outcomes (of 19) | 11 | 18 |
| … of which language = en (of 14) | 9 | 14 |
| … of which language = fr (of 2) | 1 | 1 |
| … of which language = mixed (of 1) | 0 | 1 |
| … of which language = nl (of 2) | 1 | 2 |
| Latency per need (median / max, s) | 0 | 25.1 / 31.3 |
| Tokens in / out (total) | 0 | 72,329 / 33,652 |

## Per case

| Case | Need | Lang | Kind | Expected | Baseline pick | Engine decision → top-1 (score) | Baseline | Engine | Note |
|---|---|---|---|---|---|---|---|---|---|
| T01 | Full rebrand after renovation | en | standard | match: Mira Vandenbroeck | Mira Vandenbroeck (3) | match → Mira Vandenbroeck (0.95) | ✔ | ✔ | top-1 correct (Mira Vandenbroeck, 0.95) |
| T02 | Professional photos, finally | en | standard | match: Jonas Peeters | none | match → Jonas Peeters (0.95) | ✘ | ✔ | top-1 correct (Jonas Peeters, 0.95) |
| T03 | Reduce OTA dependence | en | standard | match: Célia Fontaine | Célia Fontaine (5) | match → Célia Fontaine (0.96) | ✔ | ✔ | top-1 correct (Célia Fontaine, 0.96) |
| T04 | Website that converts | en | standard | match: Studio Klaar | Studio Klaar (2) | match → Studio Klaar (0.95) | ✔ | ✔ | top-1 correct (Studio Klaar, 0.95) |
| T05 | Fill the off-season (FR-speaking audience) | en | standard | match: Agence Littoral | Agence Littoral (1) | match → Agence Littoral (0.93) | ✔ | ✔ | top-1 correct (Agence Littoral, 0.93) |
| T06 | Fix our review profile | en | vocabulary_gap | either: Nora El Amrani / escalate | Nora El Amrani (2) | escalate → Nora El Amrani (0.55) | ✔ | ✔ | escalated (accepted) |
| T07 | LinkedIn presence for MICE | en | skill_gap | escalate | Nora El Amrani (1) | escalate → Tom Aerts (0.30) | ✘ | ✔ | escalated as expected |
| T08 | Instagram launch content | en | standard | match: Tom Aerts or Bram Willems | Tom Aerts (4) | match → Tom Aerts (0.93) | ✔ | ✔ | top-1 correct (Tom Aerts, 0.93) |
| T09 | Pre-arrival email flow | en | vocabulary_gap | match: Anke De Smet | Anke De Smet (2) | match → Anke De Smet (0.92) | ✔ | ✔ | top-1 correct (Anke De Smet, 0.92) |
| T10 | Summer occupancy idea (open-ended) | en | ambiguous | either: Agence Littoral / escalate | Agence Littoral (1) | match → Agence Littoral (0.72) | ✔ | ✔ | top-1 correct (Agence Littoral, 0.72) |
| T11 | Press push for ballroom relaunch (FR press) | en | vocabulary_gap | match: Pierre Lambert | Agence Littoral (1) | match → Pierre Lambert (0.92) | ✘ | ✔ | top-1 correct (Pierre Lambert, 0.92) |
| T12 | Be findable in three languages | en | vocabulary_gap | match: Nora El Amrani | Nora El Amrani (2) | match → Nora El Amrani (0.95) | ✔ | ✔ | top-1 correct (Nora El Amrani, 0.95) |
| T13 | Onze website converteert niet | nl | multilingual | match: Studio Klaar | Studio Klaar (1) | match → Studio Klaar (0.95) | ✔ | ✔ | top-1 correct (Studio Klaar, 0.95) |
| T14 | Instagram weer tot leven brengen | nl | multilingual | match: Tom Aerts or Bram Willems | Jonas Peeters (2) | match → Tom Aerts (0.95) | ✘ | ✔ | top-1 correct (Tom Aerts, 0.95) |
| T15 | Parcours e-mail avant le séjour | fr | multilingual | match: Anke De Smet | none | escalate → Anke De Smet (0.60) | ✘ | ✘ | escalated where a match was expected: The only consultant in the pool who covers the core skill (pre-arrival email flows and CRM) is Anke De Smet, but her languages are listed as Dutch and English only, while the brief and the hotel's positioning note make French a hard requirement (80% francophone clientele). No consultant combines email/CRM automation expertise with French. A human should ask the hotel: can they supply/validate the French copy themselves (or approve pairing Anke with a French-writing partner such as Studio Klaar's NL/FR copywriting bench), or must the whole engagement be delivered by a single French-speaking consultant? |
| T16 | Réduire notre dépendance aux OTA | fr | multilingual | match: Célia Fontaine | Célia Fontaine (3) | match → Célia Fontaine (0.97) | ✔ | ✔ | top-1 correct (Célia Fontaine, 0.97) |
| T17 | Relance presse voor de heropening van de spa (mixed FR/NL) | mixed | multilingual | match: Pierre Lambert | none | match → Pierre Lambert (0.88) | ✘ | ✔ | top-1 correct (Pierre Lambert, 0.88) |
| T18 | Ambiguous brief ("something about marketing") | en | ambiguous | escalate | Anke De Smet (1) | escalate → Mira Vandenbroeck (0.45) | ✘ | ✔ | escalated as expected |
| T19 | Empty candidate pool | en | empty_pool | escalate | Mira Vandenbroeck (3) | escalate → — | ✘ | ✔ | escalated as expected |
| T20 | Unavailable sink (task write fails) | en | sink_failure | rollback | none | rollback verified | n/a | ✔ | error surfaced (simulated: task sink unavailable); rows unchanged=True {'runs': 0, 'matches': 0, 'tasks': 0} |

## Engine reasoning per case

### T01 — Full rebrand after renovation

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Full rebrand after renovation → Mira Vandenbroeck”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Mira Vandenbroeck — 0.95: She is an expert in exactly the two core deliverables: positioning strategy and a full brand identity system, with hotel-specific proof of repositioning work in the Benelux. She also covers the 'name check (keep or evolve)' element through her naming skill, and works in Dutch as required by the brief. Being based in Antwerp she can run the discovery workshops on site.
  - gaps: No recorded PR/media-relations skill, so press placement of the launch story would need a separate partner; No evidence in her records about turnaround speed against the tight 8-weeks-before-reopening deadline; No photography/video production for the launch assets
- #2 Studio Klaar — 0.50: A multi-person design studio with NL/FR copywriting bench, which fits the tone-of-voice work in NL and EN and the roll-out of a new identity onto the website. However their documented expertise is web design and booking UX rather than brand positioning or identity systems, so they cover execution more than the strategic core.
  - gaps: No recorded positioning strategy, brand identity or naming skill — the core of the need; Day rate 800-1200 is the highest in the pool, though still within the 15k+ band; No launch PR narrative evidence
- #3 Bram Willems — 0.35: Antwerp-based and Dutch-speaking, he could produce the brand film that carries the launch story for social with a fast turnaround, which suits the tight reopening timing. He is only a partial fit: his records show no positioning, identity or naming capability.
  - gaps: No positioning, identity system or naming capability; No tone-of-voice or copywriting evidence; No press/PR distribution of the launch story
- Run 7569f97a-f9c2-402f-a38d-ba2a67a9e628; 21.2s; 4207/1762 tokens; model claude-opus-5

### T02 — Professional photos, finally

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Professional photos, finally → Jonas Peeters”; routed to e0000000-0000-0000-0000-000000000002
- #1 Jonas Peeters — 0.95: He is an exact specialist for the need: a hotel photographer who shoots exactly the subjects requested (rooms, F&B, lifestyle) for boutique properties, which matches Meridiaan's eleven rooms above its own restaurant. His evidence shows depth at scale with shot lists usable for the website and OTAs. Day rate 400-600 sits inside the 1-5k budget band and he speaks nl/en, and Ghent is within easy reach of Antwerp.
  - gaps: No stated turnaround time, so delivery speed against the 'high' urgency must be confirmed; No explicit portrait/people photography evidence for the 'family' shots requested; Photography only — does not cover rolling out the new images on the site or channels
- #2 Bram Willems — 0.50: He is Antwerp-based with hotel visual production experience and a documented fast turnaround, which suits the high urgency and local shoot logistics. However his records describe video, not stills: brand film and video editing. He would be a partial fit unless the hotel accepts video plus frame grabs instead of a proper photo set.
  - gaps: No photography skill listed — core need is still photos, not film; No evidence of interior/room or F&B stills for website or OTA use
- #3 Tom Aerts — 0.42: He produces hospitality and food visual content and is the cheapest option, which matches the small budget and the hotel's Instagram channel and F&B strength. But his documented craft is short-form video and account growth, not the professional stills needed for the website. Listed only as a nearest partial fit.
  - gaps: No hotel or interior photography evidence; Output is social video rather than website-grade room and restaurant images
- Run c8432b80-935d-4d74-a467-92e39fe6c10d; 18.9s; 3938/1350 tokens; model claude-opus-5

### T03 — Reduce OTA dependence

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Reduce OTA dependence → Célia Fontaine”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Célia Fontaine — 0.96: She is an exact specialist for the core of this need: metasearch and Google Hotel Ads with measured direct-booking results. Her ex-OTA background is directly relevant to reducing a 72% OTA share, and her direct-booking funnel work matches the members-rate/direct-channel ambition. Day rate 500-700 fits the 5-15k band.
  - gaps: Does not speak Dutch, which may matter for local Bruges stakeholder coordination; No stated experience designing loyalty/members rate programmes or PMS/booking-engine configuration; Not based in Bruges
- #2 Studio Klaar — 0.55: Direct-booking performance spend only converts if the booking flow does; Studio Klaar audits booking-flow UX with conversion tracking and builds hotel sites. This is a strong complement but not the metasearch/Google Hotel Ads core the brief asks for.
  - gaps: No metasearch or Google Hotel Ads capability listed; No paid media buying or campaign management evidence; Highest day rate band (800-1200) would consume much of the 5-15k budget
- #3 Anke De Smet — 0.45: A members rate and repeat-guest direct bookings lean on CRM and email; she is a CRM/email specialist with segmentation skills and is based in Bruges. However she covers none of the metasearch or Google Hotel Ads core of the brief.
  - gaps: No metasearch, Google Hotel Ads or paid-media capability; No direct-booking funnel or OTA-dependence evidence; Would only address the retention/members-rate slice of the need
- Run d5ad800f-8989-4f83-b279-5ac52da36857; 18.2s; 3916/1408 tokens; model claude-opus-5

### T04 — Website that converts

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Website that converts → Studio Klaar”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Studio Klaar — 0.95: Studio Klaar is the only pool member whose skills explicitly cover both sides of the need: booking-flow UX auditing and full website design/rebuild. Their booking UX evidence mentions conversion tracking, which is exactly what is needed to fix a leaking 6-step flow, and they have 15 hotel sites live on Webflow. They also work in French, which matches the hotel's 80% francophone clientele, and have an in-house NL/FR copywriting bench for rewriting the 2018-era content.
  - gaps: No explicit evidence of mobile-specific optimization work, though it is implicit in modern Webflow builds; No stated turnaround speed, so fit with the 'high' urgency needs confirming; Day-rate band 800-1200 is the highest in the pool, so a full rebuild could consume most of the 5-15k band
- #2 Célia Fontaine — 0.60: Fontaine works directly on direct-booking funnels in hospitality with measured results, so she can diagnose where bookings leak and how to shorten the path to conversion. She is French-speaking and Brussels-based, fitting the francophone corporate context. However her profile is performance marketing and metasearch rather than UX design or site rebuild, so she would cover the audit/funnel strategy but not the mobile rebuild itself.
  - gaps: No web design, UX audit or front-end build skill listed; Cannot deliver the mobile optimization or site rebuild; would need a design/build partner
- #3 Nora El Amrani — 0.45: El Amrani is a hotel-site specialist on the SEO and content side and speaks French, so she could refresh the aging 2018 content and ensure the rebuilt site stays findable. But the core of this need is booking-funnel UX and mobile conversion, which is not in her skill set.
  - gaps: No booking UX, conversion or web design skill listed; Does not cover the funnel rebuild or mobile optimization — complementary rather than primary
- Run 989bc9fb-d9ed-41b8-8697-7e0af3d4a78a; 26.6s; 4133/2021 tokens; model claude-opus-5

### T05 — Fill the off-season (FR-speaking audience)

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Fill the off-season → Agence Littoral”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Agence Littoral — 0.93: This agency is an expert in exactly the core deliverable — seasonal campaigns for coastal tourism with family-audience media buying — which is the heart of the Nov–Mar occupancy problem for Belgian coastal families. It works in French and Dutch, satisfying the French-speaking audience constraint, and is based in Ostend on the same coast as Knokke. Its local-partnerships skill also fits the floated thalasso/golf partnership ideas.
  - gaps: No stated PR/press-relations capability for the "FR media push" to lifestyle press beyond paid media buying; No evidence of spa/thalasso-specific product marketing; No documented turnaround time against the high urgency; Day rate 700-1000 is the highest-cost fit within the 5-15k band, limiting campaign days
- #2 Pierre Lambert — 0.62: The hotel's own brief explicitly floats "thalasso packages with FR media push", and this consultant is an expert in travel PR with a proven French-language press network in Wallonia, Brussels and Paris. He fits the French-speaking audience constraint natively and has placed boutique coastal properties. He covers the earned-media part of the campaign but not the paid seasonal campaign build or family media buying.
  - gaps: No seasonal campaign design or media-buying skill listed; No Dutch himself (relies on a partner for Flemish press), so the remaining 40% NL audience is indirect; Does not cover offers/packaging or occupancy-conversion mechanics toward the +15pp KPI
- #3 Célia Fontaine — 0.55: She could drive the paid-conversion layer of an off-season campaign through Google Hotel Ads and metasearch, with large managed hospitality spend, and works in French which matches the audience constraint. However her evidence is about direct-booking performance channels, not seasonal campaign concepting for families and spa weekenders.
  - gaps: No seasonal/thematic campaign creation evidence; No Dutch, so the Flemish-family portion of the audience is uncovered; No local coastal partnerships or PR capability
- Run 97f7a7f4-ad62-4135-a35e-0e9018b549d3; 26.8s; 4119/2019 tokens; model claude-opus-5

### T06 — Fix our review profile

- Decision: **escalate**; brief language detected: en; task: “Needs human review: Fix our review profile”; routed to e0000000-0000-0000-0000-000000000001
- Escalation reason: No consultant in the pool lists review response or online reputation management as a skill, and none shows evidence of managing OTA/Google review replies — that is the primary half of the need ('review-response overhaul' to lift a 4.1 average). Only the local-search half is covered (Nora El Amrani). A human should ask the hotel two questions: (1) can the scope be split, buying the local-search cleanup now from Nora and sourcing a reputation-management specialist separately; and (2) is the <1k budget firm, since at a 450-650 day rate it funds roughly one to two days, which will not cover both a response framework and a listings cleanup.
- #1 Nora El Amrani — 0.55: She is an exact fit for the local-search half of the need, with concrete evidence of cleaning up and optimising Google Business listings at scale, and her content-strategy skill could support a review tone-of-voice guide. However nothing in her record mentions review responses or reputation management, so the main driver of the brief is unproven. Her languages cover the Dutch/English audience of a Ghent station hotel.
  - gaps: No evidence of review-response writing, OTA reputation management or rating-recovery work; Day-rate band 450-650 means the <1k budget buys ~1-2 days, likely too little for both workstreams
- #2 Studio Klaar — 0.35: Their NL/FR copywriting bench could in principle produce review-response templates in the guest's language, and they work for independent hotels. But their evidenced strengths are web design and booking-flow UX, not reputation or local search, and their 800-1200 day rate does not fit a <1k budget for a multi-part job.
  - gaps: No review-response or reputation-management experience in the record; No local-search / Google Business Profile skill listed; Day-rate band 800-1200 exceeds the <1k budget for anything beyond a single day
- #3 Célia Fontaine — 0.25: As an ex-OTA account manager with metasearch expertise she understands how ratings and listing data affect OTA and Google Hotel Ads performance, which touches the local-search cleanup. But her evidenced work is paid performance and direct-booking funnels, not review responses, and she does not speak Dutch, which matters for replying to Dutch-language guest reviews in Ghent.
  - gaps: No review-response, reputation or Google Business Profile skill in the record; No Dutch, so cannot write replies to Dutch-language reviews; Day-rate band 500-700 against a <1k budget
- Run 5dc8922d-1886-4ec9-8e5b-88ee5fd4245e; 31.3s; 3893/2259 tokens; model claude-opus-5

### T07 — LinkedIn presence for MICE

- Decision: **escalate**; brief language detected: en; task: “Needs human review: LinkedIn presence for MICE”; routed to e0000000-0000-0000-0000-000000000001
- Escalation reason: No consultant in the pool covers the core of the need: LinkedIn B2B organic content for corporate/institutional event planners. The only social specialist (Tom Aerts) is a B2C short-form video creator on Instagram/TikTok with no LinkedIn or B2B evidence, and no one lists MICE, B2B lead generation or corporate social media as a skill. A human should decide whether to source a LinkedIn/B2B social specialist outside the current pool, and should ask the hotel two questions: (1) is the deliverable purely organic LinkedIn content or does it include paid LinkedIn advertising and lead capture, and (2) in which languages must the content be published for EU-institution planners (EN only, or EN/FR/NL)?
- #1 Tom Aerts — 0.30: He is the only social-media specialist in the pool and has proven ability to build hotel audiences from zero, which is the shape of this need. However his evidence is entirely B2C short-form video on Instagram and TikTok, not LinkedIn, and there is nothing in his record about B2B or corporate event-planner audiences. His day rate (300-500) fits the 1-5k budget band.
  - gaps: No LinkedIn experience listed; No B2B / MICE / corporate audience experience; No lead-generation or sales-funnel capability for meeting-room enquiries; Languages nl/en only — no French for Brussels/EU-institution audience
- #2 Nora El Amrani — 0.28: She is Brussels-based, works in the languages relevant to an EU-institution audience, and carries a content-strategy skill that could frame an editorial plan. But her documented depth is SEO and local search for multilingual hotel sites, with no LinkedIn, social publishing or B2B demand-generation evidence at all.
  - gaps: No LinkedIn or social-channel experience; No B2B/MICE audience experience; Content-strategy skill has no supporting evidence recorded; Core expertise is search, not social distribution
- #3 Mira Vandenbroeck — 0.22: She could sharpen the B2B positioning and messaging that a MICE LinkedIn program would need, based on documented repositioning work for hospitality brands. She has no social-media or LinkedIn channel skill, so she cannot run the content program itself, and her rate is at the top of the band.
  - gaps: No social media or LinkedIn execution skill; No B2B/MICE lead-generation evidence; Cannot deliver an ongoing content program, only upstream strategy; Antwerp-based, not Brussels
- Run 46ebbd43-a9fb-4db7-acd5-0be8eeb1749a; 26.2s; 3926/1980 tokens; model claude-opus-5

### T08 — Instagram launch content

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Instagram launch content → Tom Aerts”; routed to e0000000-0000-0000-0000-000000000001
- #1 Tom Aerts — 0.93: The core of the need is a sustained three-month run of short-form Instagram video, which is exactly Tom Aerts' specialism: he is described as a 'Social content creator: short-form video for hospitality' with expert-level short-form video and senior Instagram growth. His evidence of building '3 hotel accounts >50k followers' shows he can carry an ongoing hotel content programme rather than a one-off shoot. His nl/en languages fit the hotel's stated NL and EN tone of voice, and his 300-500 day rate sits comfortably inside the 1-5k band.
  - gaps: No recorded evidence of high-end design/aesthetic direction for an industrial-heritage identity; the brief says 'aesthetic matters more than volume'; Based in Leuven, not Antwerp, so repeat on-site filming means travel; No documented experience working to a group photography style guide
- #2 Bram Willems — 0.74: Bram Willems is a videographer and editor with expert video editing and senior brand-film skills, evidenced by 'Hotel brand films; 5-day turnaround', which maps well onto telling a renovation story with a crafted, aesthetic look. He is based in Antwerp, the same city as the property, making repeat renovation-progress filming easy, and speaks nl/en as the hotel requires. His 400-600 rate fits the 1-5k band.
  - gaps: No recorded Instagram or short-form/vertical social skill — his evidence is brand films and aftermovies, not a 3-month social content cadence; No social channel strategy or posting/growth capability in his records
- #3 Jonas Peeters — 0.50: Jonas Peeters is a hotel visual specialist with expert hotel photography ('40+ hotel portfolios') and senior drone video, so he could capture the renovation and the building's warehouse bones with a strong aesthetic. However his recorded skills are stills and aerials rather than short-form social video, so he covers only part of the need.
  - gaps: No short-form/vertical Instagram video skill in the records; No Instagram content strategy or three-month content-calendar capability; Ghent-based rather than Antwerp
- Run ce4b1dac-7c85-4f60-81e3-9df32d959222; 23.5s; 4182/1914 tokens; model claude-opus-5

### T09 — Pre-arrival email flow

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Pre-arrival email flow → Anke De Smet”; routed to e0000000-0000-0000-0000-000000000001
- #1 Anke De Smet — 0.92: She is the only consultant in the pool whose core practice is exactly this: pre-arrival email flows and CRM automation, with a documented pre-arrival flow template and open rate. She also covers the segmentation needed to split upsell offers from local-tips content, and she is based in Bruges, the same city as the property. Her rate band sits inside the 1-5k budget.
  - gaps: Languages listed are nl and en only — French versions of the flow would need a translator or an FR copy partner; No stated experience with upsell product/pricing setup in a PMS or booking engine
- #2 Studio Klaar — 0.45: Studio Klaar works in NL, FR and EN and has a stated copywriting bench in NL/FR, which is the exact language gap in this need, and their booking-UX work is adjacent to upsell conversion. However they list no email marketing, CRM or automation skill, so they cannot own the flow build itself. Best used as an FR/NL copy partner alongside the email specialist, though their 800-1200 rate band pushes against the 1-5k budget.
  - gaps: No email marketing, CRM or marketing-automation skill listed; No evidence of lifecycle/pre-arrival campaign work; Highest day-rate band in the pool versus a 1-5k budget
- #3 Nora El Amrani — 0.35: She covers all three required languages and works on multilingual hotel content, so she could produce the EN/FR/NL local-tips content for the flow. Her skill set is search and content strategy, not email automation, so she cannot build or segment the pre-arrival flow. Partial fit for content only.
  - gaps: No email marketing, CRM or automation experience in the record; No evidence of upsell or lifecycle campaign work
- Run d4a9307e-93ff-4c96-9441-fd1dfe884984; 26.1s; 3921/2011 tokens; model claude-opus-5

### T10 — Summer occupancy idea (open-ended)

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Summer occupancy idea → Agence Littoral”; routed to e0000000-0000-0000-0000-000000000001
- #1 Agence Littoral — 0.72: The core of the need is a seasonal campaign built on partnerships and a family audience, and this agency lists exactly those three capabilities: expert-level seasonal campaigns, senior local partnerships with tourism-board co-marketing evidence, and family-audience media buying. It works in Dutch, which suits a Leuven property. Its experience is coastal tourism where summer is peak season rather than a campus low season, and it is based in Ostend, far from Leuven's university network.
  - gaps: Based in Ostend, no recorded relationships with Leuven university or summer-school organisers; Recorded seasonal work is coastal high-season tourism, the inverse of a campus summer trough; Day-rate band 700-1000 consumes the 1-5k budget in only a few days; No content production capability recorded, while 'content' is a stated hotel weakness
- #2 Mira Vandenbroeck — 0.55: The brief is deliberately open ('open to creative'), which suits a strategist who can run a discovery workshop and define a summer positioning and offer set. She has expert positioning strategy with a published workshop methodology and works in Dutch and French across Benelux hospitality. She has no recorded campaign-execution, partnership or media-buying skills, so she would deliver the concept but not run it.
  - gaps: No seasonal campaign, partnership or media-buying skills recorded; No execution of family packages or summer-school outreach; Antwerp-based, no recorded Leuven or university network
- #3 Tom Aerts — 0.45: He is the only pool member based in Leuven and the cheapest option, and he could produce the short-form content the hotel lacks to promote summer family packages. His evidence is audience growth on hotel social accounts, not campaign strategy or partnership development. He covers the promotion layer of the need, not the offer design or partnership side.
  - gaps: No partnership, summer-school or B2B outreach skills recorded; No seasonal campaign planning or media buying; No family-package or offer-design experience recorded
- Run a832e61d-5763-4b16-a54b-5ba431571ceb; 28.6s; 3901/2179 tokens; model claude-opus-5

### T11 — Press push for ballroom relaunch (FR press)

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Press push for ballroom relaunch → Pierre Lambert”; routed to e0000000-0000-0000-0000-000000000001
- #1 Pierre Lambert — 0.92: He is a dedicated PR consultant whose core skills are media relations and travel PR, which is exactly what a 'press push' means. He works in French, writes press kits in French and has fifteen years of relationships with Wallonia, Brussels and Paris newsrooms including business titles such as L'Écho — matching the 'French-language press essential' and regional business press requirements. He is based in Liège, the same city as the property, and his 500-700 day rate fits inside the 1-5k budget band.
  - gaps: Documented placements are in lifestyle/travel press; no explicit evidence of MICE or event-planner trade media contacts; No Dutch — Flemish press would need his 'partenaire néerlandophone', though the brief does not require NL
- #2 Mira Vandenbroeck — 0.32: She works in French and is strong on brand positioning, which could shape the story angle for the ballroom relaunch, but her recorded skills are brand identity, naming and positioning strategy — not press relations. She has no evidence of journalist contacts or media placements, so she cannot deliver the core of this need alone.
  - gaps: No media relations or PR skill recorded; No journalist network or press placement evidence; Based in Antwerp, not Wallonia
- #3 Agence Littoral — 0.22: The agency speaks French and does media buying and local partnerships, which touches media work, but paid media buying is not earned press coverage. Its evidence is coastal tourism and family-audience campaigns, far from regional business and event-planner media in Liège.
  - gaps: No PR or media relations skill; media buying is paid, not earned coverage; No business or event-planner press evidence; Ostend-based, no Wallonia press network; Day rate 700-1000 consumes the 1-5k band quickly
- Run 071d71a8-f170-4b5e-9fa4-aa700cfdadcc; 24.9s; 4130/1886 tokens; model claude-opus-5

### T12 — Be findable in three languages

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Be findable in three languages → Nora El Amrani”; routed to e0000000-0000-0000-0000-000000000002
- #1 Nora El Amrani — 0.95: She is an exact specialist for this need: SEO at expert level with explicit evidence of multilingual hotel sites and hreflang, which is precisely the mechanism for making an existing Dutch site findable in other languages without a rebuild. Her local-search experience across 20+ properties also supports visibility for an Antwerp boutique hotel targeting tourists. She works in nl/fr/en, covering the Dutch source site plus two of the three target languages, and her 450-650 day rate fits the 1-5k budget band.
  - gaps: Does not list German among her languages, so DE copy/translation quality would need a native German writer or translation partner; No web development/Webflow skill listed, so any technical implementation on the site itself may need the hotel's web supplier
- #2 Studio Klaar — 0.40: Partial fit: the studio builds hotel websites and has an in-house NL/FR copywriting bench, which could produce translated language versions of existing pages. However no SEO or hreflang skill is listed, so the core search-visibility work is uncovered, and their 800-1200 day rate sits at the top of the 1-5k budget band.
  - gaps: No SEO or hreflang skill listed — the core of the need; No German language capability listed; Day rate is high against a 1-5k budget and their profile is site building, which the brief explicitly wants to avoid
- #3 Célia Fontaine — 0.30: Only a peripheral fit: she drives visibility and bookings for hotels through paid channels and metasearch, which can reach FR/EN tourist demand, but that is advertising rather than organic multilingual SEO. Nothing in her record covers hreflang, on-site content or search indexation.
  - gaps: No SEO, hreflang or multilingual site-content skill; Does not speak Dutch (the current site language) or German; Paid-media approach implies ongoing ad spend beyond the 1-5k project band
- Run c97f8751-a956-4325-a5b8-06cdfbfd3d0b; 25.1s; 3941/1870 tokens; model claude-opus-5

### T13 — Onze website converteert niet

- Decision: **match**; brief language detected: nl; task: “Engagement proposal: Onze website converteert niet → Studio Klaar”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Studio Klaar — 0.95: Studio Klaar is the only provider in the pool whose core work is exactly booking-flow UX and hotel website builds, which is what an audit plus funnel rebuild requires. Their records show booking-flow audits with conversion tracking and 15 hotel sites live, and they work in Dutch, satisfying the team's language constraint.
  - gaps: No explicit evidence of mobile-specific optimization results in the records; No stated turnaround time, so the high urgency cannot be confirmed from the records; Day-rate band 800-1200 is the highest in the pool, so the 5-15k budget limits the number of days available
- #2 Célia Fontaine — 0.45: She covers the commercial side of the need with documented direct-booking funnel results and hospitality performance marketing, so she could diagnose where bookings leak. However, her languages are French and English only, which fails the brief's explicit Dutch-speaking requirement, and her evidence is about ads and metasearch rather than site rebuild.
  - gaps: No Dutch — conflicts with 'Team spreekt Nederlands'; No web design or booking-flow UX build capability in her records; No mobile UX evidence
- #3 Nora El Amrani — 0.35: She speaks Dutch and works on hotel websites, so she could contribute to on-site content and findability around the funnel. Her documented expertise is SEO, hreflang and local search, not booking-flow UX or site rebuild, so she does not cover the core of this need.
  - gaps: No booking-flow UX or conversion-audit evidence; No website build/redesign capability in her records; Mobile funnel rebuild is outside her documented scope
- Run 25dbfb72-00e7-46f1-b9bd-11645e8ff774; 23.5s; 3945/1765 tokens; model claude-opus-5

### T14 — Instagram weer tot leven brengen

- Decision: **match**; brief language detected: nl; task: “Engagement proposal: Instagram weer tot leven brengen → Tom Aerts”; routed to e0000000-0000-0000-0000-000000000001
- #1 Tom Aerts — 0.95: Exact specialist for the need: he produces short-form video for hospitality and has demonstrably grown hotel Instagram accounts, which is precisely reviving a dormant account with a few beautiful clips per month. He works in Dutch and is based in Leuven, close enough to Ghent for recurring shoot days. His 300-500 day rate fits multiple days within the 1-5k budget over three months.
  - gaps: No stated experience with neighbourhood/destination storytelling specifically; No French, if the hotel later wants FR captions for tourists; No documented evidence for the instagram growth and tiktok skill levels beyond the follower claim
- #2 Bram Willems — 0.60: He is a videographer and editor with hotel experience, so he can shoot and cut the 'few but beautiful' clips the hotel asks for. However his evidence points at brand films and event aftermovies rather than ongoing Instagram short-form content, and there is no social-channel management in his record. Dutch-speaking and Antwerp-based, so practically reachable for Ghent shoots.
  - gaps: No Instagram or social-platform growth skill listed; Format experience is brand film/aftermovie, not a three-month recurring short-form cadence; 400-600 day rate leaves fewer shoot days inside the 1-5k band
- #3 Jonas Peeters — 0.50: He is based in Ghent itself and has drone video capability plus deep hotel visual experience, which suits filming the station neighbourhood and the property. But his core skill is stills photography for hotels rather than short-form social video, and nothing in his record covers Instagram content programmes.
  - gaps: No short-form/vertical video or Instagram skill in the record; No social account management or content-calendar experience; Primary output is photography, not the three-month video series requested
- Run a55e67c0-8ede-4171-bf4a-8a6a7a7ef37d; 20.1s; 3935/1546 tokens; model claude-opus-5

### T15 — Parcours e-mail avant le séjour

- Decision: **escalate**; brief language detected: fr; task: “Needs human review: Parcours e-mail avant le séjour”; routed to e0000000-0000-0000-0000-000000000001
- Escalation reason: The only consultant in the pool who covers the core skill (pre-arrival email flows and CRM) is Anke De Smet, but her languages are listed as Dutch and English only, while the brief and the hotel's positioning note make French a hard requirement (80% francophone clientele). No consultant combines email/CRM automation expertise with French. A human should ask the hotel: can they supply/validate the French copy themselves (or approve pairing Anke with a French-writing partner such as Studio Klaar's NL/FR copywriting bench), or must the whole engagement be delivered by a single French-speaking consultant?
- #1 Anke De Smet — 0.60: She is the only exact specialist for the core deliverable: a pre-arrival email journey with segmentation and automation tooling. Her evidence names a pre-arrival flow template with measured performance and the main marketing-automation platforms. Her day-rate band fits the 1-5k budget, but she does not list French, which the brief requires.
  - gaps: Languages listed are nl and en only — no French, while the brief requires the journey in French and Dutch and the hotel is 80% francophone; No evidence of upsell/ancillary revenue copywriting for parking, breakfast or meeting-room offers in French
- #2 Studio Klaar — 0.35: Studio Klaar has the bilingual NL/FR copy capability the brief needs and works on conversion-oriented hotel journeys, so it could produce the French and Dutch upsell content. However its listed skills are web design and booking UX, not email automation or CRM flows, so it does not cover the core deliverable. Its day-rate band also sits above the others for a 1-5k budget.
  - gaps: No email marketing, CRM or marketing-automation skill listed; No evidence of pre-arrival flow or lifecycle campaign delivery; Day rate 800-1200 consumes the 1-5k band quickly
- #3 Nora El Amrani — 0.25: She speaks French and Dutch and works as a content strategist for multilingual hotel properties, so she could shape the local-tips content in both languages. But her documented specialism is SEO and local search, with no email, CRM or automation evidence, so she cannot deliver the pre-arrival flow itself.
  - gaps: No email marketing or CRM automation skill or evidence; No upsell/ancillary campaign experience listed; Core competence is search, not lifecycle messaging
- Run f5cffeab-cd5f-4929-8f3e-168d6d2deeb2; 26.2s; 4205/2137 tokens; model claude-opus-5

### T16 — Réduire notre dépendance aux OTA

- Decision: **match**; brief language detected: fr; task: “Engagement proposal: Réduire notre dépendance aux OTA → Célia Fontaine”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Célia Fontaine — 0.97: She is an exact specialist for this need: her bio names Google Hotel Ads, metasearch and direct-booking funnels, precisely the three levers the brief asks for. Her ex-OTA account manager background is directly relevant to reducing OTA dependency, and she has measurable results on direct share. She is French-speaking and based in Brussels, satisfying both the francophone contact request and proximity to the property.
  - gaps: No recorded evidence of designing loyalty/member-rate programmes specifically, though the brief only floats this as a 'peut-être'; Does not speak Dutch, which could matter for internal NL-language coordination within the group (not requested in the brief)
- #2 Studio Klaar — 0.55: Direct bookings depend on the booking flow converting, and this studio does booking-flow UX audits with conversion tracking plus NL/FR copywriting, so they could support the conversion side of a direct-booking push. They work in French, meeting the francophone contact request. However they do not cover the paid acquisition core of the brief — no Google Hotel Ads or metasearch capability is recorded.
  - gaps: No Google Hotel Ads or metasearch experience in the records; No media buying or campaign management skill listed; Highest day-rate band in the pool (800-1200) against a 5-15k budget
- #3 Nora El Amrani — 0.45: Organic and local search visibility is a complementary channel for shifting share away from OTAs, and she is a Brussels-based French speaker with Google Business optimization across 20+ properties. But the brief explicitly asks for paid metasearch and Google Hotel Ads, which her records do not cover. She is a partial, supporting fit only.
  - gaps: No Google Hotel Ads, metasearch or paid-campaign skills recorded; No direct-booking funnel or member-rate experience in the records
- Run ae2964b2-5de4-46ea-bce5-08ff6cf12862; 18.4s; 3967/1517 tokens; model claude-opus-5

### T17 — Relance presse voor de heropening van de spa (mixed FR/NL)

- Decision: **match**; brief language detected: mixed; task: “Engagement proposal: Relance presse voor de heropening van de spa → Pierre Lambert”; routed to e0000000-0000-0000-0000-000000000001
- #1 Pierre Lambert — 0.88: He is the only consultant in the pool whose core discipline is travel PR and media relations, which is exactly what a spa reopening press push requires. His documented network covers precisely the geographies asked for — Wallonia, Brussels and Paris titles — and he has placed boutique properties including on the coast. He writes press kits in French and states he works with a Dutch-speaking partner for the Flemish press, which addresses the FR+NL requirement indirectly.
  - gaps: Does not speak Dutch himself (languages: fr, en), so the NL press kit and Flemish media outreach depend on his subcontracted Dutch-speaking partner — scope and cost of that partner should be confirmed; No documented Flemish lifestyle-press network of his own; No spa/wellness-specific PR evidence cited
- #2 Agence Littoral — 0.35: Useful only as a partial complement: the agency is bilingual FR/NL and coastal-tourism focused, which fits the Knokke off-season context and could support the Flemish side of the campaign. However its skills are seasonal campaigns, media buying and local partnerships, not earned-media PR. It has no journalist network or press-kit evidence.
  - gaps: No travel PR or media-relations skill listed; No evidence of press placements or press-kit writing; No Paris media access; Day rate 700-1000 is the highest-cost option for a 1-5k band
- #3 Mira Vandenbroeck — 0.25: She fits the 'branding' category label and works trilingually in NL/FR, so she could shape the reopening story and messaging. But the actual deliverable is press outreach and a bilingual press kit, and her evidence is brand identity and positioning work, not media relations.
  - gaps: No PR, media relations or journalist-network evidence; No press-kit or press-placement track record; Cannot deliver the core outreach to Flemish, Walloon or Parisian press
- Run 4de200cb-bf4d-4681-83ed-b947b0beeca6; 29.2s; 4151/2272 tokens; model claude-opus-5

### T18 — Ambiguous brief ("something about marketing")

- Decision: **escalate**; brief language detected: en; task: “Needs human review: Something about marketing”; routed to e0000000-0000-0000-0000-000000000002
- Escalation reason: The brief names no concrete deliverable, objective, channel or budget ("Not sure what exactly. Budget to be decided."), so the core skill to buy cannot be identified — candidates range from brand strategy to photography to social content. A human should ask the hotel: (1) what business outcome do you want (more direct bookings, more visibility, better-looking assets, more midweek occupancy)? (2) what budget range is realistic for this year? (3) is the priority fixing the visuals (profile flags 'photography' as a weakness) or defining the brand story first? Only then can a scope and a single consultant be selected.
- #1 Mira Vandenbroeck — 0.45: If the hotel needs help deciding what marketing to do at all, a discovery/positioning engagement is the natural first step, and she runs exactly that format in Dutch and is based in Antwerp like the hotel. Her evidence shows repositioning work with mid-size hospitality brands in the Benelux. However, this is an inference from the vagueness of the brief, not something the hotel asked for, and her band sits at the higher end while budget is undefined.
  - gaps: The hotel never requested brand or positioning work — this is an assumption; Day-rate band 600-800 cannot be checked against an undefined budget; Does not deliver execution such as photography, social content or campaigns
- #2 Jonas Peeters — 0.40: The hotel profile lists 'photography' as a weakness and its own positioning document says it wants to 'look as good online as the stay actually is', which points at visual assets. He is an expert hotel photographer for boutique properties and works in Dutch. But no photography brief was actually given, and scope, deliverables and budget are unknown.
  - gaps: Photography is inferred from the hotel profile, not requested in the brief; Provides assets only; no marketing strategy, channel plan or campaign execution; No budget stated to validate the 400-600 band
- #3 Tom Aerts — 0.35: Instagram is one of only two channels the hotel uses, and he is a Dutch-speaking short-form video and Instagram specialist at the lowest day rate in the pool, which suits a hotel with no marketing capacity. This remains speculative: the brief does not mention social, growth targets or content volume.
  - gaps: No social-media objective stated anywhere in the brief; Covers content execution only, not overall marketing direction, web, SEO or direct bookings; Budget not defined, so the 300-500 band cannot be confirmed as a fit
- Run 33796fae-6d6b-4d81-a863-896785ea01a2; 23.8s; 3919/1756 tokens; model claude-opus-5

### T19 — Empty candidate pool

- Decision: **escalate**; brief language detected: other; task: “Needs human review: Full rebrand after renovation”; routed to e0000000-0000-0000-0000-000000000001
- Escalation reason: Candidate pool is empty after filtering; no consultant can be proposed. A human must widen the pool or source externally.
- Run fffd946f-f965-4ab7-82e7-03f6460ef5ce; 0.0s; 0/0 tokens; model engine:empty_pool_guard

### T20 — Unavailable sink (task write fails)

error surfaced (simulated: task sink unavailable); rows unchanged=True {'runs': 0, 'matches': 0, 'tasks': 0}
