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

ALTER TABLE FilmStock
  DROP FOREIGN KEY FilmStock_filmTypeID_fk,
  ADD CONSTRAINT FilmStock_FilmTypes_fk FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE Films
  DROP FOREIGN KEY Films_filmTypeID_fk,
  ADD CONSTRAINT Films_FilmTypes_fk FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE Holders
  DROP FOREIGN KEY Holders_filmTypeID,
  ADD CONSTRAINT Holders_FilmTypes_fk FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON UPDATE CASCADE;

ALTER TABLE Exposures
  DROP FOREIGN KEY Exposures_filmTypeID_fk,
  ADD CONSTRAINT Exposures_FilmTypes_fk FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE MaxBlackTests
  DROP FOREIGN KEY mbt_filmTypes,
  ADD CONSTRAINT mbt_filmTypes FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID);

SET FOREIGN_KEY_CHECKS = 1;
