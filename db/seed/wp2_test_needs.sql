-- WP2 · Synthetic seed v1.1 — test additions for the matching engine
-- SYNTHETIC: all names fictional. Adds what WP2's test cases need and WP1's seed
-- did not have: briefs in Dutch and French (dossier §9 uncertainty 3), one
-- deliberately ambiguous brief (uncertainty 4), French-language documents, and
-- one marketing lead per organization so triggered tasks can be routed.
-- Volumes added: 2 users · 2 memberships · 6 marketing needs · 2 documents.

begin;

-- Seed v1 fix: Northgate Antwerp Docks is a Northgate property, not the independent's.
update properties set org_id = 'a0000000-0000-0000-0000-000000000001'
 where id = 'b0000000-0000-0000-0000-000000000002';

-- Routing targets: the org's marketing lead (dossier §7A step 3)
insert into users (id, email, full_name) values
  ('e0000000-0000-0000-0000-000000000001','marketing@northgate.example','Sofie Claes'),
  ('e0000000-0000-0000-0000-000000000002','lena@meridiaan.example','Lena Vermeulen');

insert into memberships (user_id, org_id, property_id, department_id, role) values
  ('e0000000-0000-0000-0000-000000000001','a0000000-0000-0000-0000-000000000001',null,null,'org_admin'),
  ('e0000000-0000-0000-0000-000000000002','a0000000-0000-0000-0000-000000000002',null,null,'org_admin');

-- Multilingual and failure-mode needs (ids continue the d… series)
insert into marketing_needs (id, property_id, title, description, category, urgency, budget_band) values
  ('d0000000-0000-0000-0000-000000000013','b0000000-0000-0000-0000-000000000008','Onze website converteert niet','Mooie site, maar de boekingen lekken weg: zes stappen om te boeken en niets werkt goed op mobiel. We willen een audit van de boekingsflow en een herbouw van de funnel. Team spreekt Nederlands.','website','high','5-15k'),
  ('d0000000-0000-0000-0000-000000000014','b0000000-0000-0000-0000-000000000003','Instagram weer tot leven brengen','Onze Instagram staat al een jaar stil. We zoeken iemand die drie maanden korte video''s maakt over de buurt rond het station en het hotel zelf. Liever weinig maar mooi.','social','normal','1-5k'),
  ('d0000000-0000-0000-0000-000000000015','b0000000-0000-0000-0000-000000000004','Parcours e-mail avant le séjour','Nos clients réservent souvent deux mois à l''avance et nous ne leur parlons jamais avant l''arrivée. Nous voulons un parcours e-mail pré-séjour avec ventes additionnelles (parking, petit-déjeuner, salle de réunion) et conseils locaux, en français et en néerlandais.','campaign','low','1-5k'),
  ('d0000000-0000-0000-0000-000000000016','b0000000-0000-0000-0000-000000000001','Réduire notre dépendance aux OTA','68 % de nos réservations passent par les OTA. Nous voulons une campagne de réservation directe : Google Hotel Ads, métamoteurs, peut-être un tarif membres. Interlocuteur francophone souhaité.','campaign','normal','5-15k'),
  ('d0000000-0000-0000-0000-000000000017','b0000000-0000-0000-0000-000000000006','Relance presse voor de heropening van de spa','Le spa rénové rouvre en mars. We willen regionale lifestyle-pers in Vlaanderen én Wallonië, plus quelques titres parisiens si possible. Persmap in FR en NL.','branding','normal','1-5k'),
  ('d0000000-0000-0000-0000-000000000018','b0000000-0000-0000-0000-000000000007','Something about marketing','We should probably do something about our marketing this year. Not sure what exactly. Budget to be decided.','general','low',null);

-- French-language unstructured documents (retrieval over non-English text)
insert into documents (org_id, property_id, consultant_id, kind, title, body, source) values
  ('a0000000-0000-0000-0000-000000000001','b0000000-0000-0000-0000-000000000004',null,'positioning','Liège Palace — note de positionnement','Le Palace est l''adresse d''affaires historique de Liège : salle de bal de 400 places, parking privé, à dix minutes de la gare des Guillemins. Notre clientèle est régionale et corporate, francophone à 80 %. Nos contenus datent de 2018 et le site web convertit mal. Toute communication vers la presse doit être disponible en français d''abord.','synthetic/liege-positioning-fr.md'),
  (null,null,'c0000000-0000-0000-0000-000000000007','bio','Pierre Lambert — profil détaillé','Consultant relations presse spécialisé voyage et lifestyle. Quinze ans de relations avec les rédactions de Wallonie, de Bruxelles et de Paris (Le Soir, L''Écho, Elle Belgique, Le Figaro Voyage). Rédige dossiers de presse en français ; travaille avec un partenaire néerlandophone pour la presse flamande. Placements récents : trois hôtels boutique en Ardenne et sur la côte.','synthetic/bio-lambert-fr.md');

commit;
