
INSERT INTO ecoride.brands( name )
VALUES ('renault'),
('peugeot'),
('toyota'),
('dacia'),
('honda'),
('fiat'),
('mercedes'),
('audi')
;


INSERT INTO ecoride.cars( model, registration, first_registration_date, energy, color, brand_id, user_id)
VALUES ( 'zoe', 'az-123-za' ,'06-05-2020', 'electrique', 'bleu', 1, 2),
( '106', 'vx-356-xa' ,'22-09-2010' , 'diesel', 'bleu', 2, 3),
( '306', 'bz-649-pv' ,'02-07-2021' , 'essence', 'vert', 2, 4),
( 'yaris', 'fd-759-bc' ,'12-12-2019' , 'hybrid', 'bleu', 1, 5),
( 'civic', 'yw-547-te' ,'17-04-2021' , 'hybrid', 'bleu', 5, 6)
;

INSERT INTO ecoride.carpoolings( departure_date, departure_time, departure_location, end_date, end_time, end_location, status, place_number, price, car_id )
VALUES('2025-02-20' ,'09:00','grandris' ,'2025-02-20','09:30','gleize' ,'done' ,2 ,4 ,1),
('2025-02-22', '09:00','grandris' ,'2025-02-22','09:30','gleize' ,'cancelled' ,2,4,2),
('2025-02-23', '09:00','grandris' ,'2025-02-23','09:30','gleize' ,'in progress' ,2 ,3 ,1),
('2025-02-23', '09:00','grandris' ,'2025-02-23','09:30','gleize' ,'in progress' ,2 ,3 ,2),
('2025-02-23', '09:00','grandris' ,'2025-02-23','09:30','gleize' ,'in progress' ,2 ,3 ,3),
('2025-02-23', '09:00','grandris' ,'2025-02-23','09:30','gleize' ,'in progress' ,2 ,3 ,4),
('2025-02-23', '08:00','grandris' ,'2025-02-23','08:30','gleize' ,'in progress' ,2 ,4 ,5),
('2025-02-24', '07:00','grandris' ,'2025-02-24','07:30','gleize' ,'pending' ,2 ,3 ,1),
('2025-02-24', '09:00','grandris' ,'2025-02-24','09:30','gleize' ,'in progress' ,2 ,5 ,5),
('2025-02-25', '08:00','grandris' ,'2025-02-25','08:30','gleize' ,'in progress' ,2 ,4 ,1),
('2025-02-25', '08:00','grandris' ,'2025-02-25','08:30','gleize' ,'in progress' ,2 ,4 ,2),
('2025-02-25', '08:00','grandris' ,'2025-02-25','08:30','gleize' ,'in progress' ,2 ,4 ,4),
('2025-02-25', '08:00','grandris' ,'2025-02-25','08:30','gleize' ,'in progress' ,2 ,4 ,5),
('2025-02-25', '09:00','grandris' ,'2025-02-25','09:30','gleize' ,'in progress' ,2 ,4 ,3),
('2025-02-26', '09:00','grandris' ,'2025-02-26','09:30','gleize' ,'pending' ,2 ,4 ,5)
;

INSERT INTO ecoride.opinions(comment, note , status) 
VALUES ( 'chauffeur au top, tr-s arrangeant',4 , 'pending' ),
('Trajet agréable et prudent je recommande',4 , 'pending' ),
('Le chauffeur est super appréciable',5 , 'accepted' ),
('Mauvaise expérience avec les autres passagers, mais le chauffeur est au top',3 , 'pending' ),
('Super agréable et les discussions sont variées',5 , 'accepted' ),
('Je reprendrais sans hésiter ce chauffeur',4 , 'pending' ),
('Trajet trs appréciable, je recommande',5 , 'accepted' ),
('Le chauffeur est très prévenant et arrangeant ',5 , 'pending' )
;

INSERT INTO ecoride.carpooling_user( carpooling_id, user_id)
VALUES ( 3, 7 ),
( 4, 9 ),
( 6, 7 ),
( 7, 8 ),
( 8, 9 )
;

INSERT INTO ecoride.role_user( role_id, user_id )
VALUES ( 3 , 7 ),
( 3, 8 ),
( 3 ,9 ),
( 3 ,3 ),
( 4, 2 ),
( 4, 3 ),
( 4, 4),
( 4, 5),
( 4, 6),
( 2, 10)
;

INSERT INTO ecoride.opinion_user( opinion_id,user_id)
VALUES (1 ,2 ),
( 2, 2 ),
( 3, 4 ),
( 4, 5 ),
( 5, 6 ),
( 6 ,4 ),
( 7, 6 ),
( 8, 3 )
;
