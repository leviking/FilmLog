ALTER TABLE FilmTypes
  MODIFY COLUMN kind enum('Color Negative','Black & White Negative','Color Slide','Black & White Slide', 'Motion Picture Color Negative') DEFAULT NULL,

INSERT INTO FilmTypes (filmBrandID, name, iso, kind)
  VALUES (1, 'Vision3 500T/5219', 500, 'Motion Picture Color Negative');

INSERT INTO FilmTypes (filmBrandID, name, iso, kind)
  VALUES (1, 'Vision3 200T/5213', 200, 'Motion Picture Color Negative');

INSERT INTO FilmTypes (filmBrandID, name, iso, kind)
  VALUES (1, 'Vision3 250D/5207', 250, 'Motion Picture Color Negative');

INSERT INTO FilmTypes (filmBrandID, name, iso, kind)
  VALUES (1, 'Vision3 50D/5203', 50, 'Motion Picture Color Negative');
