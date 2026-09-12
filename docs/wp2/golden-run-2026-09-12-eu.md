# WP2 golden-set run — 2026-09-12 11:27

Model: claude-opus-5. Cases: 20 (19 scored + 1 rollback).

## Summary

| | Keyword baseline | AI engine |
|---|---|---|
| Correct outcomes (of 19) | 11 | 19 |
| … of which language = en (of 14) | 9 | 14 |
| … of which language = fr (of 2) | 1 | 2 |
| … of which language = mixed (of 1) | 0 | 1 |
| … of which language = nl (of 2) | 1 | 2 |
| Latency per need (median / max, s) | 0 | 24.0 / 89.3 |
| Tokens in / out (total) | 0 | 72,351 / 34,833 |

## Per case

| Case | Need | Lang | Kind | Expected | Baseline pick | Engine decision → top-1 (score) | Baseline | Engine | Note |
|---|---|---|---|---|---|---|---|---|---|
| T01 | Full rebrand after renovation | en | standard | match: Mira Vandenbroeck | Mira Vandenbroeck (3) | match → Mira Vandenbroeck (0.95) | ✔ | ✔ | top-1 correct (Mira Vandenbroeck, 0.95) |
| T02 | Professional photos, finally | en | standard | match: Jonas Peeters | none | match → Jonas Peeters (0.95) | ✘ | ✔ | top-1 correct (Jonas Peeters, 0.95) |
| T03 | Reduce OTA dependence | en | standard | match: Célia Fontaine | Célia Fontaine (5) | match → Célia Fontaine (0.96) | ✔ | ✔ | top-1 correct (Célia Fontaine, 0.96) |
| T04 | Website that converts | en | standard | match: Studio Klaar | Studio Klaar (2) | match → Studio Klaar (0.95) | ✔ | ✔ | top-1 correct (Studio Klaar, 0.95) |
| T05 | Fill the off-season (FR-speaking audience) | en | standard | match: Agence Littoral | Agence Littoral (1) | match → Agence Littoral (0.94) | ✔ | ✔ | top-1 correct (Agence Littoral, 0.94) |
| T06 | Fix our review profile | en | vocabulary_gap | either: Nora El Amrani / escalate | Nora El Amrani (2) | match → Nora El Amrani (0.70) | ✔ | ✔ | top-1 correct (Nora El Amrani, 0.70) |
| T07 | LinkedIn presence for MICE | en | skill_gap | escalate | Nora El Amrani (1) | escalate → Nora El Amrani (0.38) | ✘ | ✔ | escalated as expected |
| T08 | Instagram launch content | en | standard | match: Tom Aerts or Bram Willems | Tom Aerts (4) | match → Tom Aerts (0.92) | ✔ | ✔ | top-1 correct (Tom Aerts, 0.92) |
| T09 | Pre-arrival email flow | en | vocabulary_gap | match: Anke De Smet | Anke De Smet (2) | match → Anke De Smet (0.88) | ✔ | ✔ | top-1 correct (Anke De Smet, 0.88) |
| T10 | Summer occupancy idea (open-ended) | en | ambiguous | either: Agence Littoral / escalate | Agence Littoral (1) | match → Agence Littoral (0.82) | ✔ | ✔ | top-1 correct (Agence Littoral, 0.82) |
| T11 | Press push for ballroom relaunch (FR press) | en | vocabulary_gap | match: Pierre Lambert | Agence Littoral (1) | match → Pierre Lambert (0.88) | ✘ | ✔ | top-1 correct (Pierre Lambert, 0.88) |
| T12 | Be findable in three languages | en | vocabulary_gap | match: Nora El Amrani | Nora El Amrani (2) | match → Nora El Amrani (0.95) | ✔ | ✔ | top-1 correct (Nora El Amrani, 0.95) |
| T13 | Onze website converteert niet | nl | multilingual | match: Studio Klaar | Studio Klaar (1) | match → Studio Klaar (0.95) | ✔ | ✔ | top-1 correct (Studio Klaar, 0.95) |
| T14 | Instagram weer tot leven brengen | nl | multilingual | match: Tom Aerts or Bram Willems | Jonas Peeters (2) | match → Tom Aerts (0.95) | ✘ | ✔ | top-1 correct (Tom Aerts, 0.95) |
| T15 | Parcours e-mail avant le séjour | fr | multilingual | either: Anke De Smet / escalate | none | escalate → Anke De Smet (0.60) | ✘ | ✔ | escalated (accepted) |
| T16 | Réduire notre dépendance aux OTA | fr | multilingual | match: Célia Fontaine | Célia Fontaine (3) | match → Célia Fontaine (0.97) | ✔ | ✔ | top-1 correct (Célia Fontaine, 0.97) |
| T17 | Relance presse voor de heropening van de spa (mixed FR/NL) | mixed | multilingual | match: Pierre Lambert | none | match → Pierre Lambert (0.86) | ✘ | ✔ | top-1 correct (Pierre Lambert, 0.86) |
| T18 | Ambiguous brief ("something about marketing") | en | ambiguous | escalate | Anke De Smet (1) | escalate → Mira Vandenbroeck (0.45) | ✘ | ✔ | escalated as expected |
| T19 | Empty candidate pool | en | empty_pool | escalate | Mira Vandenbroeck (3) | escalate → — | ✘ | ✔ | escalated as expected |
| T20 | Unavailable sink (task write fails) | en | sink_failure | rollback | none | rollback verified | n/a | ✔ | error surfaced (simulated: task sink unavailable); rows unchanged=True {'runs': 0, 'matches': 0, 'tasks': 0} |

## Engine reasoning per case

### T01 — Full rebrand after renovation

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Full rebrand after renovation → Mira Vandenbroeck”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Mira Vandenbroeck — 0.95: She is a brand strategist who delivers exactly the three things asked for: positioning, identity system and naming (the 'name check, keep or evolve'). Her evidence shows repeated hotel rebranding work in the Benelux, including a harbour-hotel repositioning that fits the industrial-dock context. She works in Dutch and is based in Antwerp, satisfying the Dutch-speaking-team and proximity constraints, and her 600-800 day rate sits comfortably inside a 15k+ budget.
  - gaps: No recorded PR/media-relations skill, so the press side of the launch story may need a separate partner; No explicit evidence on turnaround speed against the 8-weeks-before-reopening deadline
- #2 Studio Klaar — 0.50: The studio can execute the visible expression of a new brand — website and NL/FR copywriting — and works in Dutch, which satisfies the language constraint. However its recorded skills are web design, booking UX and copywriting, not positioning, identity systems or naming, so it covers only the downstream half of the need. Its 800-1200 day rate is still within a 15k+ budget.
  - gaps: No positioning strategy or brand identity skill on record; No naming experience recorded; No launch narrative or press-story evidence
- #3 Bram Willems — 0.35: He could produce the brand film that carries a launch story and is Antwerp-based with fast turnaround, which suits the high urgency. But his records show only video production skills, with nothing on positioning, identity or naming, so he is at best a production add-on to the rebrand rather than the lead.
  - gaps: No brand strategy, positioning or identity-system capability; No naming or tone-of-voice work recorded; Cannot deliver the core of the rebrand alone
- Run ca143aef-f19f-4399-89df-817591eb64be; 19.6s; 4204/1526 tokens; model claude-opus-5

### T02 — Professional photos, finally

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Professional photos, finally → Jonas Peeters”; routed to e0000000-0000-0000-0000-000000000002
- #1 Jonas Peeters — 0.95: He is an exact specialist for this need: a hotel photographer who shoots exactly the subjects listed in the brief (rooms, F&B, lifestyle) for boutique properties, which matches Meridiaan's eleven-room family hotel above its own restaurant. His evidence shows depth (40+ hotel portfolios) and deliverables aimed at web/OTA use, which is what the hotel means by 'look as good online as the stay actually is'. He speaks Dutch and English and his 400-600 day rate fits the 1-5k band.
  - gaps: Records state no explicit turnaround time, so speed against the 'high' urgency is unverified; Based in Ghent rather than Antwerp, so travel may be needed; No stated portrait/family-portrait specialism, though 'lifestyle' is listed
- #2 Bram Willems — 0.50: He is the nearest local visual-content alternative: Antwerp-based, fast, and experienced with hotel visual storytelling, which would suit the family and restaurant story. However his documented skills are film and editing, not still photography, so he only partially covers a photo-library need. His day rate fits the budget band and he speaks Dutch.
  - gaps: No evidence of still photography for rooms, F&B or portraits — the core deliverable of this brief; Video output would not directly replace the outdated site photos
- #3 Tom Aerts — 0.35: He produces hospitality and food visual content and could generate social-ready material for an Instagram-led hotel, but his documented craft is short-form video, not a professional still-photo library for the website. He is the cheapest option and Dutch-speaking, so he is a fallback for channel content rather than the asset refresh the brief asks for.
  - gaps: No hotel or interior still-photography evidence; Does not cover rooms/restaurant/family photography for the website
- Run c454cdf1-dd47-4c28-8562-8b22422b4642; 20.2s; 3942/1508 tokens; model claude-opus-5

### T03 — Reduce OTA dependence

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Reduce OTA dependence → Célia Fontaine”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Célia Fontaine — 0.96: She is an exact specialist for this need: her bio names Google Hotel Ads, metasearch and direct-booking funnels, which are precisely the three levers the brief asks for. Her evidence shows measured direct-share uplift and large-scale hospitality media management, and she previously worked on the OTA side, which is directly relevant to reducing OTA dependence. Her day rate of 500-700 fits comfortably inside the 5-15k budget band.
  - gaps: No Dutch in her languages (fr, en) — a constraint only if local NL-language landing pages or NL copy are required; No recorded experience designing a members/loyalty rate programme or the PMS/booking-engine side of it; Not based in Bruges (Brussels)
- #2 Studio Klaar — 0.55: A direct-booking push also depends on the site converting the traffic, and this studio does booking-flow UX for independent hotels with conversion tracking. They cover the on-site half of the funnel and can produce NL/FR copy for a members-rate page. They do not, however, run metasearch or Google Hotel Ads themselves.
  - gaps: No metasearch or Google Hotel Ads capability listed; No paid-media buying or campaign management evidence; Highest day-rate band in the pool (800-1200), which consumes budget quickly
- #3 Anke De Smet — 0.45: A members rate needs a CRM and email engine behind it, and she is an expert in exactly that, with segmentation and win-back flows and measured open rates. She is also based in Bruges, so she can work closely with the property. She covers none of the metasearch or Google Hotel Ads core, so she is a complement rather than the lead.
  - gaps: No metasearch, Google Hotel Ads or paid-media skills; No direct-booking funnel or OTA-shift evidence; Cannot lead the campaign; only supports the members-rate/CRM component
- Run 1eaa98c0-a7b0-47f6-80ff-8e979423b123; 23.9s; 3917/1800 tokens; model claude-opus-5

### T04 — Website that converts

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Website that converts → Studio Klaar”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Studio Klaar — 0.95: Studio Klaar is a design studio whose core offer is exactly this need: websites and booking-flow UX for independent hotels, with documented booking-flow audits including conversion tracking. Their expert-level web design is evidenced by 15 live hotel sites and Webflow certification, so they can both audit and rebuild the funnel. Their NL/FR copywriting bench covers the francophone clientele of the Liège property.
  - gaps: No explicit mobile-optimization evidence listed, though implied by web design practice; Based in Mechelen, not Liège — on-site presence in Wallonia not documented; No stated turnaround time against the 'high' urgency of this need
- #2 Célia Fontaine — 0.60: Célia Fontaine specialises in direct-booking funnels with measurable results, which addresses the conversion/booking-leak side of the brief, and works in French from Brussels. However her profile is performance marketing (Hotel Ads, metasearch) rather than UX design and site rebuild, so she would complement rather than replace a design partner.
  - gaps: No web design, UX audit or mobile optimization skills in her record; Cannot deliver the site rebuild itself
- #3 Nora El Amrani — 0.40: Nora El Amrani works on multilingual hotel websites and could support the rebuilt site's search visibility and content structure in FR/NL/EN. Her record covers SEO and content strategy, not booking-flow UX or front-end rebuild, so she is only a partial, supporting fit for this need.
  - gaps: No booking UX or conversion-funnel redesign capability documented; No website build/design skill listed
- Run 183a3518-3854-4460-8d42-ca3c4d0c14e6; 23.8s; 4135/1904 tokens; model claude-opus-5

### T05 — Fill the off-season (FR-speaking audience)

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Fill the off-season → Agence Littoral”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Agence Littoral — 0.94: Agence Littoral is an expert in exactly the core deliverable — seasonal campaigns for coastal tourism with family-audience media buying — which maps directly onto the Nov–Mar family/spa weekend push. It works in French and Dutch, satisfying the 60% French-speaking audience constraint, and is based on the same coastline (Ostend) with tourism-board co-marketing experience that suits the floated golf and local partnership ideas.
  - gaps: No recorded spa/thalasso-specific campaign experience; No documented PR/press-placement capability for the FR media push floated in the hotel brief; Highest day-rate band in the shortlist (700-1000), so budget buys fewer days; No English-language capability listed, if any group-level reporting requires it
- #2 Pierre Lambert — 0.62: The hotel brief explicitly floats "thalasso packages with FR media push", and Pierre Lambert is an expert in travel PR with a documented French-language press network. He can deliver the earned-media component of the seasonal campaign for the French-speaking audience, but not the campaign concept or paid media buying itself.
  - gaps: No seasonal campaign design or media-buying skills recorded; Does not speak Dutch himself — "travaille avec un partenaire néerlandophone pour la presse flamande" — so Flemish family audience coverage depends on a partner; PR alone will not cover the paid-channel and packaging work needed to move occupancy by 15pp
- #3 Célia Fontaine — 0.55: Célia Fontaine could handle the paid-performance and booking-conversion side of an off-season push, with proven hospitality ad spend management and direct-booking results, and she works in French for the majority French-speaking audience. She is a partial fit only: her records show performance/metasearch execution, not seasonal campaign concepting, packaging or local partnerships.
  - gaps: No seasonal or off-season campaign concept experience recorded; No Dutch, so cannot address the Dutch-speaking share of Belgian coastal families directly; No local partnership or PR capability for the golf/tourism-board ideas in the brief
- Run 71c1930e-aa17-4c17-850b-e675e330afba; 89.3s; 4120/2250 tokens; model claude-opus-5

### T06 — Fix our review profile

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Fix our review profile → Nora El Amrani”; routed to e0000000-0000-0000-0000-000000000001
- #1 Nora El Amrani — 0.70: She is the only consultant in the pool with documented local-search work, which is exactly the 'local-search cleanup' half of the need: her local search skill is evidenced by 'Google Business optimization for 20+ properties'. Her senior content strategy skill plus nl/fr/en languages make her a credible owner of a Dutch/English review-response framework and tone-of-voice templates. Her 450-650 day-rate band fits inside the <1k budget for a scoped one-to-two-day engagement.
  - gaps: No record of online reputation management or review-response experience specifically — her evidence is SEO/local listings, not OTA and Google review handling.; No evidence of working on ratings recovery or responding to historical complaints, which is the part the hotel frames as the main problem.; At 450-650/day the <1k budget covers only about 1.5 days: enough for an audit plus response playbook, not for ongoing response execution.
- Run e29213aa-b996-41c7-882e-b99f8227d697; 31.1s; 3894/2158 tokens; model claude-opus-5

### T07 — LinkedIn presence for MICE

- Decision: **escalate**; brief language detected: en; task: “Needs human review: LinkedIn presence for MICE”; routed to e0000000-0000-0000-0000-000000000001
- Escalation reason: No consultant in the pool covers the core skill: LinkedIn B2B content programming for a corporate/MICE buyer audience. The only social specialist (Tom Aerts) is a B2C short-form video creator on Instagram/TikTok with no LinkedIn or B2B evidence, and the only content strategist (Nora El Amrani) is an SEO/local-search specialist whose content-strategy skill carries no evidence and no B2B or social-platform track record. A human should ask the hotel two things: (1) is this an organic LinkedIn content programme, a paid LinkedIn Ads/lead-gen programme, or both — since that changes whether a content creator or a performance marketer is needed; and (2) in which languages the B2B content must run (EN only, or EN+FR for EU-institution planners). If sourcing is needed, the pool should be extended with a B2B/LinkedIn social specialist.
- #1 Nora El Amrani — 0.38: She is the closest match on the content side and is Brussels-based with the language range (fr/en) that EU-institution planners would need, and she holds a 'content strategy' skill at senior level. However that skill has no supporting evidence, and all her documented work is search-related rather than social or B2B.
  - gaps: No LinkedIn or any social-platform skill listed; No B2B or MICE/corporate-buyer experience in the records; Content strategy skill has no evidence attached; all evidence is SEO/local search ('Multilingual hotel sites, hreflang specialist', 'Google Business optimization for 20+ properties')
- #2 Tom Aerts — 0.30: He is the only social-media specialist in the pool and has proven ability to grow hotel audiences from zero, which is what the hotel lacks. But his documented platforms and formats are consumer-facing Instagram and TikTok short-form video, not a LinkedIn B2B programme, and he does not speak French.
  - gaps: No LinkedIn skill or evidence; channels listed are Instagram and TikTok only; No B2B, MICE or corporate event-planner audience experience; Languages nl/en only — no French for EU-institution audiences; No evidence of lead generation or sales-oriented content, only follower growth
- #3 Mira Vandenbroeck — 0.25: She could define the positioning and messaging platform that a MICE B2B channel would be built on, backed by a documented positioning methodology and hospitality repositioning work. She cannot deliver the LinkedIn content programme itself, as no social or channel-execution skill appears in her record.
  - gaps: No social media or LinkedIn execution skill; No B2B/MICE demand-generation evidence; Day rate 600-800 would consume much of the 1-5k band on strategy alone, leaving execution unfunded
- Run 274bf83a-77db-4db8-8a9b-dab3be9fafbb; 28.9s; 3927/2332 tokens; model claude-opus-5

### T08 — Instagram launch content

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Instagram launch content → Tom Aerts”; routed to e0000000-0000-0000-0000-000000000001
- #1 Tom Aerts — 0.92: Tom Aerts is a dedicated short-form video creator for hospitality, which is exactly the deliverable (3 months of short-form video for Instagram). He has proven Instagram outcomes with hotel accounts and works in NL and EN, matching the hotel's NL/EN tone of voice. His day rate is the lowest in the pool, which helps stretch a 1-5k budget across a three-month programme.
  - gaps: Based in Leuven, not Antwerp, so on-site shooting days require travel; Evidence emphasises follower growth/volume rather than the high-end design aesthetic the brief prioritises; No stated experience with brand-identity or launch narrative work, which the reopening brief also mentions
- #2 Bram Willems — 0.72: Bram Willems is an Antwerp-based videographer and editor with hotel brand films in his portfolio, so he can shoot and cut the renovation story with high production value on the hotel's doorstep. His expert-level video editing supports an aesthetic-first output. He is a film producer rather than a social-channel specialist, so the Instagram content strategy would need to come from elsewhere.
  - gaps: No stated Instagram or short-form/vertical social specialism or growth evidence; No social content-calendar or channel-management capability for a 3-month programme
- #3 Jonas Peeters — 0.45: Jonas Peeters brings strong hotel visual craft and some motion capability through certified drone video, which could document the renovation's architecture. However his core skill is stills photography for boutique properties, not the short-form social video the brief asks for. He would be a partial fit, best as a complement rather than the lead.
  - gaps: No short-form/vertical video or Instagram content skill listed; No evidence of running a multi-month social content programme
- Run 30b52f5f-fe95-45e0-9bba-f7f5469aea49; 21.2s; 4179/1529 tokens; model claude-opus-5

### T09 — Pre-arrival email flow

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Pre-arrival email flow → Anke De Smet”; routed to e0000000-0000-0000-0000-000000000001
- #1 Anke De Smet — 0.88: She is an exact specialist for the core of this need: CRM and email with an explicitly documented pre-arrival flow capability and measured performance. She works in the hotel's own city, Bruges, and her day rate band fits the 1-5k budget. The only shortfall is French: her listed languages are Dutch and English, so the FR version of the flow would need an external copy partner.
  - gaps: Languages listed are 'nl, en' only — no French, while the brief asks for an EN/FR/NL flow; No stated upsell-merchandising or local-content production skill beyond email/CRM execution
- #2 Studio Klaar — 0.42: Studio Klaar covers the trilingual writing side the brief demands and works in NL, FR and EN, with a copywriting bench that could produce the pre-arrival and local-tips content. However, their listed skills are web design, booking UX and copywriting — no email marketing, CRM or automation-flow capability is recorded. Their day rate band is also the highest in the pool relative to a 1-5k budget.
  - gaps: No email marketing, CRM or marketing-automation skill listed — the core of the need is uncovered; High day-rate band (800-1200) consumes much of a 1-5k budget
- #3 Nora El Amrani — 0.33: She is trilingual plus Arabic and is a content strategist, so she could shape the local-tips content in EN/FR/NL. Her recorded expertise is SEO, hreflang and local search, not lifecycle email or CRM automation, so she cannot build the pre-arrival flow itself.
  - gaps: No email marketing, CRM or pre-arrival automation experience in her record; Her evidence is search-oriented ('Multilingual hotel sites, hreflang specialist'), not guest-lifecycle messaging
- Run c7661975-707e-42a9-8a49-fa5c5d76804b; 26.8s; 3922/1978 tokens; model claude-opus-5

### T10 — Summer occupancy idea (open-ended)

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Summer occupancy idea → Agence Littoral”; routed to e0000000-0000-0000-0000-000000000001
- #1 Agence Littoral — 0.82: The core of this need is a seasonal low-occupancy campaign built on partnerships and family offers, and this agency lists exactly that combination: expert-level seasonal campaigns, senior local partnerships and family-audience media buying. Its stated profile is 'seasonal campaigns, local partnerships, family-audience media buying', which maps one-to-one onto the brief's 'partnerships, summer schools, family packages'. It works in Dutch and French, so it can operate in the Leuven market.
  - gaps: Partnership evidence is tourism-board co-marketing on the coast, not university/summer-school partnerships in a campus city; Based in Ostend, no evidenced local network in Leuven; Day rate 700-1000 against a 1-5k budget limits the engagement to a few days, so execution beyond concept may need to be handled in-house; No evidence on content/photography production, which the hotel lists as a weakness
- #2 Célia Fontaine — 0.52: If the hotel decides the summer gap is best closed with paid demand capture rather than partnerships, she is the strongest performance option: expert in Google Hotel Ads and metasearch with evidenced direct-booking uplift, and the hotel already uses google_ads as a channel. She would push a family/summer package into market, but she does not cover campaign concepting or partnership building.
  - gaps: No seasonal campaign concepting or partnership skills listed; Languages fr/en only — no Dutch, a drawback for local Leuven partnerships and NL-language creative; Media budget within a 1-5k total band would be very thin after her day rate
- #3 Tom Aerts — 0.50: He is the only Leuven-based consultant in the pool and the cheapest (300-500), which fits the small budget, and his expert short-form video plus Instagram/TikTok growth could carry a summer family-package message and also address the hotel's 'content' weakness. However he is a content creator, not a campaign or partnership strategist, so he covers promotion rather than the offer design the brief asks for.
  - gaps: No seasonal campaign, partnership or packaging skills listed; No media buying or paid distribution evidence; Any photography/video must be checked against the group style guide (natural light, no HDR, people anonymous)
- Run ed423c6c-cbea-455f-bdc3-0852b81b4c26; 33.9s; 3902/2431 tokens; model claude-opus-5

### T11 — Press push for ballroom relaunch (FR press)

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Press push for ballroom relaunch → Pierre Lambert”; routed to e0000000-0000-0000-0000-000000000001
- #1 Pierre Lambert — 0.88: The need is a press push, i.e. media relations, and Pierre Lambert is an expert-level PR consultant with documented placements in FR/BE press. He works in French and writes press kits in French, which satisfies the hard French-language constraint from both the brief and the hotel's positioning note. He is based in Liège itself and has fifteen years of relationships with Walloon and Brussels newsrooms, including the business title L'Écho, which matches the regional business-press target.
  - gaps: His documented network is travel and lifestyle press; event-planner / MICE trade media are not named in his records; Records mention a Dutch-speaking partner for Flemish press, so Dutch-language outreach would be subcontracted (not required here); No evidence of managing the launch event itself or producing relaunch photography
- #2 Mira Vandenbroeck — 0.40: She is a partial fit only: the need is filed under branding and she is an expert brand strategist who can run discovery and positioning work in French, useful for shaping the relaunch story for a 'Grand address for business'. However nothing in her records covers press relations or journalist placement, which is the core of this need.
  - gaps: No media relations or PR skill or evidence; No journalist network in Wallonia or business/event media; Based in Antwerp, not the Liège region
- #3 Agence Littoral — 0.32: The agency works in French and has senior media-buying and local-partnership capability, which could support paid visibility around the reopening. But its evidence is coastal, seasonal and family-audience tourism, and paid media buying is not the same as earned press coverage, so it does not cover the core PR need.
  - gaps: No PR or media-relations skill listed; media buying is paid, not earned coverage; No evidence of business press or event-planner media contacts; Focus and evidence are coastal/family tourism, not regional corporate events; based in Ostend, far from Liège; Day rate band 700-1000 leaves little room in a 1-5k budget for a multi-day push
- Run ea5f7a40-1eb9-483a-a8f3-0a29827aea6d; 23.2s; 4132/1918 tokens; model claude-opus-5

### T12 — Be findable in three languages

- Decision: **match**; brief language detected: en; task: “Engagement proposal: Be findable in three languages → Nora El Amrani”; routed to e0000000-0000-0000-0000-000000000002
- #1 Nora El Amrani — 0.95: She is an exact specialist for this need: her bio and expert-level SEO skill both cite multilingual hotel sites and hreflang, which is precisely the technical layer required to serve EN/FR/DE versions on an existing Dutch site. Her local-search evidence across 20+ properties matches the goal of being found by city tourists. Her day-rate band of 450-650 fits comfortably within the 1-5k budget, and she works in Dutch, French and English for the content side.
  - gaps: Does not list German among her languages, so German copy/translation may need an external translator; No web-development skill listed, so any technical implementation on the site itself may require the hotel's developer
- #2 Studio Klaar — 0.50: As a hotel web studio with a NL/FR copywriting bench they could implement multilingual page structures and produce translated content on an existing build. However no SEO or hreflang skill is listed, which is the core of the need, and their 800-1200 day rate sits at the top of the 1-5k budget.
  - gaps: No SEO or hreflang skill in the record — the core of the need is uncovered; No German-language capability listed (nl, fr, en only); Day-rate band 800-1200 limits how many days fit in a 1-5k budget
- #3 Célia Fontaine — 0.35: She could improve visibility for foreign-language tourists through paid and metasearch channels, and works in FR/EN, but her evidence is entirely performance marketing rather than organic multilingual search. She is a fallback if the hotel would accept paid visibility instead of SEO.
  - gaps: No SEO, hreflang or multilingual site skill listed; No Dutch or German language capability (fr, en only), limiting work on the existing Dutch site
- Run 26ecf7a9-84bd-421c-9dca-c1959d94d7bf; 21.8s; 3945/1731 tokens; model claude-opus-5

### T13 — Onze website converteert niet

- Decision: **match**; brief language detected: nl; task: “Engagement proposal: Onze website converteert niet → Studio Klaar”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Studio Klaar — 0.95: Studio Klaar is a design studio whose core offer is exactly booking-flow UX and hotel websites, which is what a booking-funnel audit plus rebuild requires. They document booking-flow audits with conversion tracking and 15 live hotel sites, and they work in Dutch, satisfying the team's language constraint. Their day rate is the highest in the pool, so the 5-15k band limits the engagement to a focused audit and funnel rebuild rather than an unlimited scope.
  - gaps: No documented turnaround times, so the 'high' urgency cannot be verified from the records; At 800-1200/day the 5-15k budget covers only a limited number of days; a full multi-page site rebuild may exceed it; No evidence of paid-media/metasearch work if the leaking bookings also need acquisition-side fixes
- #2 Célia Fontaine — 0.45: She specialises in direct-booking funnels with measured results, which is the commercial half of the need. However, she is a performance marketer rather than a UX/web builder, so she could audit and optimise the funnel but not rebuild the mobile site. Critically, she speaks only French and English while the hotel team works in Dutch.
  - gaps: No Dutch — fails the stated language constraint; No web design or booking-UX build capability for the mobile rebuild
- #3 Nora El Amrani — 0.35: She works on hotel websites and speaks Dutch, so she could support the site work from a content and search angle. Her documented expertise is SEO, hreflang and local search, not booking-flow UX or funnel rebuilding. She would be a complement, not the owner of this need.
  - gaps: No booking-flow UX or conversion audit evidence; No web build / mobile redesign capability
- Run 7e48f94e-ef56-4cb4-b5a9-c5cabfcf7dc9; 23.4s; 3946/1796 tokens; model claude-opus-5

### T14 — Instagram weer tot leven brengen

- Decision: **match**; brief language detected: nl; task: “Engagement proposal: Instagram weer tot leven brengen → Tom Aerts”; routed to e0000000-0000-0000-0000-000000000001
- #1 Tom Aerts — 0.95: This is exactly his specialism: he is a social content creator producing short-form video for hospitality and has demonstrably revived/grown hotel Instagram accounts. His expert-level short-form video plus senior Instagram growth covers both the content production and the account revival the hotel asks for. He works in Dutch and his 300-500 day rate fits comfortably in the 1-5k band for a low-volume three-month cadence from nearby Leuven.
  - gaps: No documented evidence of neighbourhood/destination storytelling specifically, only hotel and food content; No record of working within a group photography style guide (natural light, no HDR, anonymous people); Based in Leuven, not Ghent, so travel for repeat local shoots is a minor factor
- #2 Bram Willems — 0.72: He is a videographer and editor with hotel brand film experience, so he can deliver the 'few but beautiful' visual quality the hotel wants, in Dutch and within budget. However his evidence points to brand films and event aftermovies rather than ongoing Instagram short-form output or account management.
  - gaps: No recorded Instagram or social-account growth skill — the channel-revival part of the need is uncovered; No evidence of vertical short-form/Reels formats specifically; Antwerp-based, so recurring station-neighbourhood shoots require travel
- #3 Jonas Peeters — 0.55: He is based in Ghent, which is ideal for repeated shoots in the station neighbourhood, and he is an expert hotel visual specialist with certified drone video including city aerials. But his core record is photography rather than short-form social video, and he has no Instagram content or growth evidence.
  - gaps: No short-form/Reels video production skill on record; No Instagram or social channel management/growth experience recorded; Would likely need to be paired with someone for editing and posting cadence over the three months
- Run 85a2a58e-84d0-4b7c-a20b-b6ccf70114ab; 24.0s; 3936/1841 tokens; model claude-opus-5

### T15 — Parcours e-mail avant le séjour

- Decision: **escalate**; brief language detected: fr; task: “Needs human review: Parcours e-mail avant le séjour”; routed to e0000000-0000-0000-0000-000000000001
- Escalation reason: The only consultant who covers the core of the need (pre-arrival email flow / CRM) is Anke De Smet, whose languages are listed as 'nl, en' — she does not cover French, which the brief states as a requirement and which the hotel document reinforces ('francophone à 80 %'). No other consultant in the pool has any email marketing, CRM or automation skill: the FR/NL-capable profiles cover brand strategy (Mira Vandenbroeck), SEO/content (Nora El Amrani), web design and booking UX with NL/FR copywriting (Studio Klaar) or seasonal campaigns and media buying (Agence Littoral). A human should ask the hotel: can the French copy be produced on the hotel side or by a paired FR copywriter (e.g. Studio Klaar's 'copywriting nl/fr' bench) while Anke De Smet builds and segments the flow, or must the consultant personally work in French? That answer decides whether this can be matched or needs a new FR-speaking CRM profile.
- #1 Anke De Smet — 0.60: She is the only exact specialist for the core deliverable: her bio names pre-arrival flows and her email marketing skill is rated expert with a concrete pre-arrival evidence metric, and she can handle the segmentation and tooling side. However her listed languages are Dutch and English only, so she cannot produce the French half of the flow for an 80% francophone clientele without a French-language partner.
  - gaps: No French language capability, while the brief requires FR and NL and the hotel is 80% francophone; No record of French copywriting support or a FR partner; Based in Bruges, no stated experience with Liège/Wallonia corporate audiences
- #2 Studio Klaar — 0.32: Studio Klaar meets the language constraint (nl, fr, en) and has a stated NL/FR copywriting bench, which would cover the bilingual upsell and local-tips content. But their skills are web design and booking-flow UX, with no email marketing, CRM or automation evidence, so they do not cover the core pre-arrival flow build.
  - gaps: No email marketing, CRM or marketing-automation skill listed; No pre-arrival flow or segmentation evidence; Day rate 800-1200 would consume most of the 1-5k budget band
- #3 Nora El Amrani — 0.28: She satisfies the FR/NL language requirement and has senior content strategy experience that could shape the local-tips content of the journey. Her documented specialism is SEO, hreflang and local search, not email automation, so the core flow and upsell mechanics are uncovered.
  - gaps: No email marketing or CRM tooling skill or evidence; No pre-arrival flow or upsell campaign experience in the records
- Run ea80e388-1c39-48cb-8035-ed1125c5674f; 32.2s; 4207/2439 tokens; model claude-opus-5

### T16 — Réduire notre dépendance aux OTA

- Decision: **match**; brief language detected: fr; task: “Engagement proposal: Réduire notre dépendance aux OTA → Célia Fontaine”; routed to e0000000-0000-0000-0000-000000000001
- Group sign-off flagged (org rule applied from documents)
- #1 Célia Fontaine — 0.97: She is an exact specialist for this need: her bio names Google Hotel Ads, metasearch and direct-booking funnels, which are precisely the three levers the brief asks for. Her evidence shows measurable direct-share uplift and large-scale hospitality media spend, and her ex-OTA background fits the goal of reducing OTA dependency. She works in French and is based in Brussels, satisfying the francophone contact and proximity preferences.
  - gaps: No recorded experience designing or configuring a member/loyalty rate scheme in the PMS/booking engine; No Dutch — if Flemish-language campaign assets are needed later, a partner would be required
- #2 Studio Klaar — 0.45: Direct-booking performance only converts if the booking flow works, and this studio audits booking-flow UX with conversion tracking and builds hotel websites, with NL/FR copywriting. They could support the landing pages and member-rate presentation side of the campaign. They do not, however, run Google Hotel Ads or metasearch campaigns, which is the core of the brief.
  - gaps: No Google Hotel Ads or metasearch bidding capability listed; No paid-media or channel-mix experience recorded; Day rate 800-1200 is the highest in the pool against a 5-15k campaign budget
- #3 Nora El Amrani — 0.40: She is Brussels-based and francophone, and her local-search and multilingual SEO work supports organic direct bookings, which is an adjacent route to reducing OTA dependency. Her Google Business optimization across 20+ properties helps direct visibility. She has no recorded paid metasearch or Google Hotel Ads experience, so she cannot deliver the campaign core alone.
  - gaps: No Google Hotel Ads or metasearch campaign management in her skills; No paid-media buying or direct-booking funnel evidence; No member-rate or loyalty programme experience recorded
- Run bed489e1-c6d7-4f57-a13e-ea45d57fcc3f; 21.0s; 3968/1480 tokens; model claude-opus-5

### T17 — Relance presse voor de heropening van de spa (mixed FR/NL)

- Decision: **match**; brief language detected: mixed; task: “Engagement proposal: Relance presse voor de heropening van de spa → Pierre Lambert”; routed to e0000000-0000-0000-0000-000000000001
- #1 Pierre Lambert — 0.86: He is the only consultant in the pool whose core practice is travel PR and media relations, with documented placements in FR/BE lifestyle press - exactly the 'relance presse' the spa reopening needs. His detailed profile names fifteen years of relationships with newsrooms in Wallonia, Brussels and Paris, covering both the Walloon and Parisian targets in the brief. For the Dutch-language side he writes press kits in French and works with a Dutch-speaking partner for the Flemish press, and his day-rate band 500-700 sits inside the 1-5k budget.
  - gaps: Speaks only FR and EN: the Dutch press kit and Flemish media outreach depend on a subcontracted Dutch-speaking partner rather than on him directly; No recorded evidence of his own placements in Flemish lifestyle titles; No spa/wellness-specific PR case in the records
- #2 Agence Littoral — 0.42: The agency works bilingually in FR and NL and is based on the coast, which fits the Knokke reopening and the bilingual press kit requirement. However its documented strengths are seasonal campaigns, media buying and tourism-board partnerships - paid and partnership work, not earned press relations. It could support a FR/NL reopening campaign around the spa but not the journalist outreach itself.
  - gaps: No PR or media-relations skill listed; media buying is paid placement, not press outreach; No evidence of a journalist network in Wallonia or Paris; Day rate 700-1000 consumes the 1-5k budget faster than a freelance alternative
- #3 Mira Vandenbroeck — 0.35: She is trilingual NL/FR/EN and could shape the reopening story and messaging for a bilingual press kit, which is one component of the need. Her recorded expertise is brand identity and positioning for Benelux hotels, not press relations, so she cannot deliver the journalist outreach that is the core of this brief. She would be a supporting rather than a lead choice.
  - gaps: No PR, media relations or press-office experience in the records; No journalist contacts in Wallonia, Flanders or Paris evidenced; Day rate 600-800 for work that only covers the messaging layer of the need
- Run ac995430-ee44-4633-9302-44b0fa966bcf; 27.7s; 4152/2212 tokens; model claude-opus-5

### T18 — Ambiguous brief ("something about marketing")

- Decision: **escalate**; brief language detected: en; task: “Needs human review: Something about marketing”; routed to e0000000-0000-0000-0000-000000000002
- Escalation reason: The brief does not state what the hotel actually wants to buy ("Not sure what exactly") and gives no budget, so no single deliverable can be scoped or priced. A human should ask Hotel Meridiaan: (1) what outcome matters most this year — more direct bookings, better photography/visual content, a repositioned brand, or more Instagram reach; (2) what budget range is realistic, since candidate day rates range from 300-500 to 800-1200; (3) whether they want a short paid discovery/audit first to define the scope. The hotel's own documents point to visual assets ("photography" listed as a weakness; "look as good online as the stay actually is") and no internal marketing capacity, but that is inference, not a stated need.
- #1 Mira Vandenbroeck — 0.45: If the hotel needs help deciding what to do at all, a discovery-led brand strategist is the closest fit: she runs structured discovery workshops in Dutch and is based in Antwerp like the hotel. Her hospitality repositioning track record matches a boutique, family-run property that wants to look as good online as the stay is. But she is a strategy/identity specialist, not an answer to an undefined need, and her 600-800 band is unverified against a budget that is explicitly "to be decided".
  - gaps: Does not deliver execution channels the hotel may actually need: photography, social content, SEO, paid media or email; No evidence of a diagnostic marketing audit or channel plan as a paid product; Day rate 600-800 unverifiable against an undecided budget for an eleven-room hotel
- #2 Jonas Peeters — 0.35: The hotel's profile names photography as a weakness and its positioning document asks to "look as good online as the stay actually is", which points to a hotel photo shoot as the most concrete latent need. Peeters shoots exactly this segment, including F&B, which is the hotel's stated strength. This is an inferred need, not a requested one, so the fit is partial.
  - gaps: Covers only visual assets; no strategy, channel plan or campaign execution; The need for photography is inferred from hotel profile weaknesses, never requested in the brief; No marketing capacity is provided to use the assets afterwards
- #3 Tom Aerts — 0.30: Instagram is one of only two channels the hotel uses, and Aerts is a short-form video and Instagram growth specialist for hospitality and food, matching the hotel's foodie audience and F&B strength. He is also the lowest day-rate option, which suits an undecided budget. However, this addresses one channel only and the brief never asks for social work.
  - gaps: Single-channel scope; no brand, web, SEO, email or paid coverage; Does not address the hotel's photography weakness for web/OTA assets; Need is assumed from the hotel's channel list, not stated in the brief
- Run 0137158a-df71-4a97-b846-946975799806; 25.5s; 3923/2000 tokens; model claude-opus-5

### T19 — Empty candidate pool

- Decision: **escalate**; brief language detected: other; task: “Needs human review: Full rebrand after renovation”; routed to e0000000-0000-0000-0000-000000000001
- Escalation reason: Candidate pool is empty after filtering; no consultant can be proposed. A human must widen the pool or source externally.
- Run f3c22663-0d40-4daf-99c5-9b8589b17601; 0.0s; 0/0 tokens; model engine:empty_pool_guard

### T20 — Unavailable sink (task write fails)

error surfaced (simulated: task sink unavailable); rows unchanged=True {'runs': 0, 'matches': 0, 'tasks': 0}
