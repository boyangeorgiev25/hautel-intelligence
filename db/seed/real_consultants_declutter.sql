-- 28 Sep 2026: remove engagement-specific lines from the real roster that name the very briefs
-- being tested (Cocoon, Sapphire, Pandox), so WP2/WP3 scores rest on skills, not on lookup.
begin;
update consultants set bio = replace(bio, ' Videographer on the Cocoon Hotels refresh (Sep 2026).', ' Videographer on hotel shoots.')
 where dataset='real' and full_name='Boyan Georgiev';
update consultant_expertise set evidence='Videography on hotel shoots (freelance agreement, 2026)'
 where consultant_id=(select id from consultants where dataset='real' and full_name='Boyan Georgiev') and skill='videography';
update consultants set bio = replace(bio, ' Owner of the Pandox Belgium shotlist and visual proposals per property.', ' Owns shotlists and visual proposals per property for hotel-group shoots.')
 where dataset='real' and full_name='Aaron Cimanga';
update consultant_expertise set evidence='Shotlists and visual proposals per property for hotel-group shoots (project briefings)'
 where consultant_id=(select id from consultants where dataset='real' and full_name='Aaron Cimanga') and skill='concept development';
update consultant_expertise set evidence='''Creative all-rounder'' (Hotel Indigo testimonial); on-site creative direction in agency offers'
 where consultant_id=(select id from consultants where dataset='real' and full_name='Anton Verheyden') and skill='creative direction';
commit;
select full_name, left(bio, 120) from consultants where dataset='real' and full_name in ('Boyan Georgiev','Aaron Cimanga');
