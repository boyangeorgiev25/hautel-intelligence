-- WP1 · Synthetic seed dataset (v1)
-- SYNTHETIC: all names fictional. Stands in until real Drive/client data arrives;
-- structure mirrors what we asked Anton for (consultant list, hotel profiles, briefs).
-- Volumes: 2 orgs · 8 properties · 8 hotel profiles · 10 consultants · 27 expertise
-- rows · 12 marketing needs · 6 unstructured documents.

begin;

-- Organizations: one group, one independent
insert into organizations (id, name, kind) values
  ('a0000000-0000-0000-0000-000000000001','Northgate Hospitality Group','group'),
  ('a0000000-0000-0000-0000-000000000002','Hotel Meridiaan (independent)','independent');

insert into properties (id, org_id, name, region) values
  ('b0000000-0000-0000-0000-000000000001','a0000000-0000-0000-0000-000000000001','Northgate Brussels Central','Brussels'),
  ('b0000000-0000-0000-0000-000000000002','a0000000-0000-0000-0000-000000000002','Northgate Antwerp Docks','Antwerp'),
  ('b0000000-0000-0000-0000-000000000003','a0000000-0000-0000-0000-000000000001','Northgate Ghent Station','Ghent'),
  ('b0000000-0000-0000-0000-000000000004','a0000000-0000-0000-0000-000000000001','Northgate Liège Palace','Liège'),
  ('b0000000-0000-0000-0000-000000000005','a0000000-0000-0000-0000-000000000001','Northgate Bruges Old Town','Bruges'),
  ('b0000000-0000-0000-0000-000000000006','a0000000-0000-0000-0000-000000000001','Northgate Knokke Beach','Knokke'),
  ('b0000000-0000-0000-0000-000000000007','a0000000-0000-0000-0000-000000000002','Hotel Meridiaan','Antwerp'),
  ('b0000000-0000-0000-0000-000000000008','a0000000-0000-0000-0000-000000000001','Northgate Leuven Campus','Leuven');

insert into hotel_profiles (property_id, segment, audience, positioning, channels, strengths, weaknesses) values
  ('b0000000-0000-0000-0000-000000000001','business','EU-institution travellers, MICE','Efficient, connected, quietly premium','{google_ads,linkedin,direct}','{location,meeting_rooms}','{weekend_occupancy,social_presence}'),
  ('b0000000-0000-0000-0000-000000000002','boutique','Design-conscious city travellers','Industrial heritage, local culture','{instagram,pr}','{design,f&b}','{corporate_bookings,ota_dependence}'),
  ('b0000000-0000-0000-0000-000000000003','budget','Rail commuters, weekend tourists','Clean, fast, fair','{ota,google_ads}','{price,location}','{brand_awareness,reviews}'),
  ('b0000000-0000-0000-0000-000000000004','business','Regional corporate, events','Grand address for business','{linkedin,email}','{ballroom,parking}','{aging_content,website_conversion}'),
  ('b0000000-0000-0000-0000-000000000005','boutique','International leisure couples','Storybook stay in the old town','{instagram,ota,pr}','{location,reviews}','{seasonality,direct_bookings}'),
  ('b0000000-0000-0000-0000-000000000006','resort','Belgian coastal families, golfers','Effortless seaside weekends','{facebook,email,pr}','{beach_access,spa}','{off_season_occupancy}'),
  ('b0000000-0000-0000-0000-000000000007','boutique','Culture travellers, foodies','Family-run, fiercely local','{instagram,word_of_mouth}','{f&b,personal_service}','{no_marketing_capacity,photography}'),
  ('b0000000-0000-0000-0000-000000000008','budget','Visiting academics, student families','Smart stay next to campus','{google_ads,university_partnerships}','{price,quiet}','{summer_occupancy,content}');

insert into consultants (id, full_name, kind, bio, languages, region, day_rate_band) values
  ('c0000000-0000-0000-0000-000000000001','Mira Vandenbroeck','freelancer','Brand strategist, ex-agency lead. Ten years repositioning mid-size hospitality and retail brands across Benelux; runs discovery workshops in Dutch or French and delivers full identity systems.','{nl,fr,en}','Antwerp','600-800'),
  ('c0000000-0000-0000-0000-000000000002','Jonas Peeters','freelancer','Hotel photographer. Shoots rooms, F&B and lifestyle for boutique properties; portfolio includes 40+ hotels; drone-certified.','{nl,en}','Ghent','400-600'),
  ('c0000000-0000-0000-0000-000000000003','Célia Fontaine','freelancer','Performance marketer focused on hospitality: Google Hotel Ads, metasearch, direct-booking funnels. Ex-OTA account manager.','{fr,en}','Brussels','500-700'),
  ('c0000000-0000-0000-0000-000000000004','Studio Klaar','agency','Six-person design studio. Websites and booking-flow UX for independent hotels; Webflow + headless builds; strong copywriting bench in NL/FR.','{nl,fr,en}','Mechelen','800-1200'),
  ('c0000000-0000-0000-0000-000000000005','Tom Aerts','freelancer','Social content creator: short-form video for hospitality and food. Built three hotel accounts past 50k followers.','{nl,en}','Leuven','300-500'),
  ('c0000000-0000-0000-0000-000000000006','Anke De Smet','freelancer','CRM & email specialist: guest segmentation, pre-arrival flows, win-back campaigns. Mailchimp/Klaviyo/ActiveCampaign.','{nl,en}','Bruges','400-600'),
  ('c0000000-0000-0000-0000-000000000007','Pierre Lambert','freelancer','PR consultant, travel media. Places boutique properties in FR/BE lifestyle press; strong journalist network in Wallonia and Paris.','{fr,en}','Liège','500-700'),
  ('c0000000-0000-0000-0000-000000000008','Nora El Amrani','freelancer','SEO and content strategist; multilingual hotel sites; hreflang and local-search specialist.','{nl,fr,en,ar}','Brussels','450-650'),
  ('c0000000-0000-0000-0000-000000000009','Bram Willems','freelancer','Videographer + editor; hotel brand films and event aftermovies; fast turnaround.','{nl,en}','Antwerp','400-600'),
  ('c0000000-0000-0000-0000-000000000010','Agence Littoral','agency','Coastal-tourism marketing agency: seasonal campaigns, local partnerships, family-audience media buying.','{fr,nl}','Ostend','700-1000');

insert into consultant_expertise (consultant_id, skill, level, evidence) values
  ('c0000000-0000-0000-0000-000000000001','brand identity','expert','Rebranded 12 Benelux hotels; case: harbour hotel repositioning +18% ADR'),
  ('c0000000-0000-0000-0000-000000000001','positioning strategy','expert','Discovery-workshop methodology, published toolkit'),
  ('c0000000-0000-0000-0000-000000000001','naming','senior',null),
  ('c0000000-0000-0000-0000-000000000002','hotel photography','expert','40+ hotel portfolios; OTA-optimized shot lists'),
  ('c0000000-0000-0000-0000-000000000002','drone video','senior','Certified; coastal + city aerials'),
  ('c0000000-0000-0000-0000-000000000003','google hotel ads','expert','Managed €1.2M/yr hospitality spend'),
  ('c0000000-0000-0000-0000-000000000003','metasearch','expert',null),
  ('c0000000-0000-0000-0000-000000000003','direct booking funnels','senior','Avg +22% direct share across 8 clients'),
  ('c0000000-0000-0000-0000-000000000004','web design','expert','15 hotel sites live; Webflow certified'),
  ('c0000000-0000-0000-0000-000000000004','booking ux','senior','Booking-flow audits with conversion tracking'),
  ('c0000000-0000-0000-0000-000000000004','copywriting nl/fr','senior',null),
  ('c0000000-0000-0000-0000-000000000005','short-form video','expert','3 hotel accounts >50k followers'),
  ('c0000000-0000-0000-0000-000000000005','instagram growth','senior',null),
  ('c0000000-0000-0000-0000-000000000005','tiktok','senior',null),
  ('c0000000-0000-0000-0000-000000000006','email marketing','expert','Pre-arrival flow template, 38% open avg'),
  ('c0000000-0000-0000-0000-000000000006','guest segmentation','senior',null),
  ('c0000000-0000-0000-0000-000000000006','crm setup','senior','Mailchimp/Klaviyo/ActiveCampaign'),
  ('c0000000-0000-0000-0000-000000000007','travel pr','expert','Placements: 30+ features in FR/BE lifestyle press'),
  ('c0000000-0000-0000-0000-000000000007','media relations','expert',null),
  ('c0000000-0000-0000-0000-000000000008','seo','expert','Multilingual hotel sites, hreflang specialist'),
  ('c0000000-0000-0000-0000-000000000008','content strategy','senior',null),
  ('c0000000-0000-0000-0000-000000000008','local search','senior','Google Business optimization for 20+ properties'),
  ('c0000000-0000-0000-0000-000000000009','brand film','senior','Hotel brand films; 5-day turnaround'),
  ('c0000000-0000-0000-0000-000000000009','video editing','expert',null),
  ('c0000000-0000-0000-0000-000000000010','seasonal campaigns','expert','Coastal tourism; family audience media buying'),
  ('c0000000-0000-0000-0000-000000000010','local partnerships','senior','Tourism-board co-marketing'),
  ('c0000000-0000-0000-0000-000000000010','media buying','senior',null);

insert into marketing_needs (id, property_id, title, description, category, urgency, budget_band) values
  ('d0000000-0000-0000-0000-000000000001','b0000000-0000-0000-0000-000000000002','Full rebrand after renovation','We reopen in spring after a full renovation. Current identity feels dated against the new industrial-heritage interior. Need positioning, identity system and launch story. Dutch-speaking team.','branding','high','15k+'),
  ('d0000000-0000-0000-0000-000000000002','b0000000-0000-0000-0000-000000000007','Professional photos, finally','Everything on our site is phone photos from 2019. Rooms, restaurant, the family. Small budget but this blocks everything else.','photography','high','1-5k'),
  ('d0000000-0000-0000-0000-000000000003','b0000000-0000-0000-0000-000000000005','Reduce OTA dependence','72% of bookings via OTAs. Want a direct-booking push: metasearch, Google Hotel Ads, maybe a members rate.','campaign','normal','5-15k'),
  ('d0000000-0000-0000-0000-000000000004','b0000000-0000-0000-0000-000000000004','Website that converts','Site is beautiful but bookings leak: 6-step booking flow, no mobile optimization. Want a UX audit and rebuild of the funnel.','website','high','5-15k'),
  ('d0000000-0000-0000-0000-000000000005','b0000000-0000-0000-0000-000000000006','Fill the off-season','November–March occupancy at 34%. Need a seasonal campaign for Belgian families + spa weekenders; French-speaking audience matters.','campaign','high','5-15k'),
  ('d0000000-0000-0000-0000-000000000006','b0000000-0000-0000-0000-000000000003','Fix our review profile','4.1 average dragged by old complaints. Want a review-response overhaul and local-search cleanup.','content','normal','<1k'),
  ('d0000000-0000-0000-0000-000000000007','b0000000-0000-0000-0000-000000000001','LinkedIn presence for MICE','We sell meeting rooms but have no B2B channel. Want a LinkedIn content program targeting EU-institution event planners.','social','normal','1-5k'),
  ('d0000000-0000-0000-0000-000000000008','b0000000-0000-0000-0000-000000000002','Instagram launch content','For the reopening: 3 months of short-form video telling the renovation story. Aesthetic matters more than volume.','social','normal','1-5k'),
  ('d0000000-0000-0000-0000-000000000009','b0000000-0000-0000-0000-000000000005','Pre-arrival email flow','Guests book 60+ days out and we never talk to them until check-in. Want a pre-arrival upsell + local-tips flow in EN/FR/NL.','campaign','low','1-5k'),
  ('d0000000-0000-0000-0000-000000000010','b0000000-0000-0000-0000-000000000008','Summer occupancy idea','Campus empties in July–August and so do we. Open to creative: partnerships, summer schools, family packages.','campaign','normal','1-5k'),
  ('d0000000-0000-0000-0000-000000000011','b0000000-0000-0000-0000-000000000004','Press push for ballroom relaunch','Renovated ballroom reopens in October. Want regional business press + event-planner media coverage. French-language press essential.','branding','normal','1-5k'),
  ('d0000000-0000-0000-0000-000000000012','b0000000-0000-0000-0000-000000000007','Be findable in three languages','Tourists search in EN/FR/DE and we only exist in Dutch. Need multilingual SEO without rebuilding the whole site.','website','normal','1-5k');

insert into documents (org_id, property_id, kind, title, body, source) values
  ('a0000000-0000-0000-0000-000000000001','b0000000-0000-0000-0000-000000000002','brief','Antwerp Docks reopening brief','The hotel closes in January for the final renovation phase. The new interior leans into the warehouse bones of the building: steel, brick, oak. We want the brand to stop apologizing for being industrial and start owning it. Target guest: the design-aware traveller who books the Hoxton or Mama Shelter in other cities. Deliverables discussed: name check (keep or evolve), identity, tone of voice in NL and EN, launch narrative for press and social. Budget approved at director level. Timing: identity ready 8 weeks before reopening.','synthetic/brief-docks.md'),
  ('a0000000-0000-0000-0000-000000000002','b0000000-0000-0000-0000-000000000007','positioning','Meridiaan — who we are','Second-generation family hotel, eleven rooms above our own restaurant. Guests choose us because Lena remembers their names and the sourdough is ours. We will never be a chain and do not want to look like one. What we need is to look as good online as the stay actually is.','synthetic/meridiaan-positioning.md'),
  ('a0000000-0000-0000-0000-000000000001','b0000000-0000-0000-0000-000000000006','brief','Knokke off-season brief','Occupancy Nov-Mar: 34% vs 81% in season. Spa utilization near zero on weekdays. Ideas floated: thalasso packages with FR media push, family "sea in winter" weekends, golf partnerships. Audience is 60% French-speaking. KPI: +15pp off-season occupancy within two seasons.','synthetic/knokke-brief.md'),
  (null,null,'case_study','Consultant case — harbour hotel rebrand','Mira Vandenbroeck repositioned a 45-room harbour hotel: discovery workshops with staff and returning guests, new identity system, tone of voice in NL/FR, launch PR. Result: +18% ADR within a year, direct bookings +9pp. Full deliverable list and timeline attached in original.','synthetic/case-mira.md'),
  (null,null,'bio','Studio Klaar — extended profile','Studio Klaar is a six-person studio in Mechelen. Hotel work: 15 sites live, average build 9 weeks, all with integrated booking-engine UX and multilingual copy in NL/FR/EN. They decline projects without direct access to the booking-engine configuration — lesson from two failed handovers.','synthetic/klaar-bio.md'),
  ('a0000000-0000-0000-0000-000000000001',null,'brief','Group content standards note','All Northgate properties must keep photography within the group style guide (natural light, no HDR, people present but anonymous). Any rebrand or campaign at property level needs group marketing sign-off before external spend above €5k.','synthetic/northgate-standards.md');

commit;
