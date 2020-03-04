SET FOREIGN_KEY_CHECKS = 0;

RENAME TABLE FilmTypes TO GlobalFilmTypes;
RENAME TABLE FilmBrands TO GlobalFilmBrands;

CREATE TABLE FilmTypes (
    userID INT UNSIGNED NOT NULL,
    filmTypeID SMALLINT UNSIGNED NOT NULL,
    name varchar(64) NOT NULL,
    iso smallint unsigned,
    kind enum('Color Negative','Black & White Negative','Color Slide','Black & White Slide', 'Motion Picture Color Negative') DEFAULT NULL,
    PRIMARY KEY (userID, filmTypeID),
    UNIQUE KEY user_name_iso_uq (userID, name, iso),
    CONSTRAINT FilmTypes_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

INSERT INTO FilmTypes
SELECT 1, filmTypeID, CONCAT(brand, ' ', name), iso, kind
FROM GlobalFilmTypes
JOIN GlobalFilmBrands ON GlobalFilmBrands.filmBrandID = GlobalFilmTypes.filmBrandID;

SET FOREIGN_KEY_CHECKS = 1;
