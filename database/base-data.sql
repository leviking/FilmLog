INSERT INTO `Migrations` VALUES ('20180811-22'),
('20180910-1'),
('20180911-1'),
('20180925'),
('20181003'),
('20181027'),
('20181130'),
('20181204'),
('20181206'),
('20181206-2'),
('20181208'),
('20190109'),
('20190115'),
('20190122'),
('20190124'),
('20190201'),
('20190510'),
('20190511'),
('20190512'),
('20190607'),
('20190608');

INSERT INTO `GlobalFilmBrands` VALUES (6,'Adox'),
(9,'Arista.EDU'),
(4,'Bergger'),
(7,'Cinestill'),
(10,'Ferrania'),
(8,'Fomapan'),
(2,'Fuji'),
(3,'Ilford'),
(5,'JCH'),
(1,'Kodak'),
(11,'Rollei'),
(12,'Lomography'),
(13,'Ultrafine'),
(14,'CatLABS');

INSERT INTO `GlobalFilmTypes`
VALUES (1,1,'Ektar',100,'Color Negative'),
(2,1,'Portra',160,'Color Negative'),
(3,1,'Portra',400,'Color Negative'),
(4,1,'Portra',800,'Color Negative'),
(5,1,'T-Max',100,'Black & White Negative'),
(6,1,'T-Max',400,'Black & White Negative'),
(7,1,'Tri-X',320,'Black & White Negative'),
(8,1,'Tri-X',400,'Black & White Negative'),
(9,2,'Velvia',50,'Color Slide'),
(10,2,'Velvia',100,'Color Slide'),
(11,3,'Delta',100,'Black & White Negative'),
(12,3,'Delta',400,'Black & White Negative'),
(13,3,'Delta',3200,'Black & White Negative'),
(14,3,'HP5+',400,'Black & White Negative'),
(15,4,'Pancro',400,'Black & White Negative'),
(16,3,'FP4+',125,'Black & White Negative'),
(17,5,'StreetPan',400,'Black & White Negative'),
(18,6,'CMS',20,'Black & White Negative'),
(19,3,'PAN F Plus',50,'Black & White Negative'),
(20,7,'800T',800,'Color Negative'),
(21,9,'Ultra',400,'Black & White Negative'),
(22,9,'Ultra',100,'Black & White Negative'),
(23,9,'Ultra',200,'Black & White Negative'),
(24,10,'P30',80,'Black & White Negative'),
(25,1,'T-Max',3200,'Black & White Negative'),
(27,11,'RPX',25,'Black & White Negative'),
(28,2,'Superia XTRA',400,'Color Negative'),
(29,2,'Acros',100,'Black & White Negative'),
(30,2,'Provia 100F',100,'Color Slide'),
(31,1,'Gold',200,'Color Negative'),
(32,1,'Gold',400,'Color Negative'),
(33,11,'Infrared',400,'Black & White Negative'),
(34,1,'Max',800,'Color Negative'),
(35,1,'Portra NC',160,'Color Negative'),
(36,1,'Ektachrome E100D',100,'Color Slide'),
(37,1,'Vision3 500T/5219',500,'Motion Picture Color Negative'),
(38,1,'Vision3 200T/5213',200,'Motion Picture Color Negative'),
(39,1,'Vision3 250D/5207',250,'Motion Picture Color Negative'),
(40,1,'Vision3 50D/5203',50,'Motion Picture Color Negative'),
(41,12,'Color',800,'Color Negative'),
(42,13,'Xtreme',100,'Black & White Negative'),
(43,13,'Xtreme',400,'Black & White Negative'),
(44,6,'CHS ii',100,'Black & White Negative'),
(45,14,'X FILM', 80, 'Black & White Negative'),
(46,6,'Silvermax',100,'Black & White Negative'),
(47,6,'HR-50',50,'Black & White Negative'),
(48,3,'Ortho Plus',80,'Black & White Negative'),
(49,2,'Pro 400H', 400, 'Color Negative'),
(50,13,'Ortho Litho', 10, 'Black & White Negative'),
(51, 12,'Metropolis',400,'Color Negative'),
(52, 2,'Acros II',100,'Black & White Negative');


INSERT INTO PaperFilters (name) VALUES ('00');
INSERT INTO PaperFilters (name) VALUES ('0');
INSERT INTO PaperFilters (name) VALUES ('1/2');
INSERT INTO PaperFilters (name) VALUES ('1');
INSERT INTO PaperFilters (name) VALUES ('1 1/2');
INSERT INTO PaperFilters (name) VALUES ('2');
INSERT INTO PaperFilters (name) VALUES ('2 1/2');
INSERT INTO PaperFilters (name) VALUES ('3');
INSERT INTO PaperFilters (name) VALUES ('3 1/2');
INSERT INTO PaperFilters (name) VALUES ('4');
INSERT INTO PaperFilters (name) VALUES ('4 1/2');
INSERT INTO PaperFilters (name) VALUES ('5');
INSERT INTO PaperFilters (name) VALUES ('Split-Grade');

INSERT INTO FilmSizes VALUES (1, '35mm 12', 'Small', 'Roll');
INSERT INTO FilmSizes VALUES (2, '35mm 24', 'Small', 'Roll');
INSERT INTO FilmSizes VALUES (3, '35mm 36', 'Small', 'Roll');
INSERT INTO FilmSizes VALUES (4, '35mm Hand Roll', 'Small', 'Roll');
INSERT INTO FilmSizes VALUES (5, '120', 'Medium', 'Roll');
INSERT INTO FilmSizes VALUES (6, '220', 'Medium', 'Roll');
INSERT INTO FilmSizes VALUES (7, '4x5', 'Large', 'Sheet');
INSERT INTO FilmSizes VALUES (8, '5x7', 'Large', 'Sheet');
INSERT INTO FilmSizes VALUES (9, '8x10', 'Large', 'Sheet');
INSERT INTO FilmSizes VALUES (10,'11x14', 'Ultra-Large', 'Sheet');

INSERT INTO PaperDevelopers VALUES (1, 'Ilford Multigrade', '9');
INSERT INTO PaperDevelopers VALUES (2, 'Ilford Multigrade', '14');
INSERT INTO PaperDevelopers VALUES (3, 'Dektol', '0');
INSERT INTO PaperDevelopers VALUES (4, 'Dektol', '1');
INSERT INTO PaperDevelopers VALUES (5, 'Dektol', '2');
INSERT INTO PaperDevelopers VALUES (6, 'Dektol', '3');
