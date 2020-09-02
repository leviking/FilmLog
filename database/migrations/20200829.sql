CREATE TABLE DevRecipes (
    userID INT UNSIGNED NOT NULL,
    devRecipeID SMALLINT UNSIGNED NOT NULL,
    developer VARCHAR(32) NOT NULL,
    type ENUM ('Black and White', 'C-41', 'ECN2', 'E-6') NOT NULL DEFAULT 'Black and White',
    dilution TINYINT NOT NULL DEFAULT 0,
    time SMALLINT UNSIGNED NOT NULL,
    temperature TINYINT UNSIGNED NOT NULL,
    stop ENUM('Stop Bath', 'Water') NOT NULL DEFAULT 'Stop Bath',
    agitation ENUM('Rotary', 'Hand-Inversions', 'Dip and Dunk', 'Tray') NOT NULL DEFAULT 'Hand-Inversions',
    description TEXT,
    PRIMARY KEY (userID, devRecipeID),
    CONSTRAINT DevRecipes_Users_fk FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE FilmTests (
  userID INT UNSIGNED NOT NULL,
  filmTestID INT UNSIGNED NOT NULL,
  devRecipeID SMALLINT UNSIGNED NOT NULL,
  filmTypeID SMALLINT UNSIGNED NOT NULL,
  enlargerID TINYINT UNSIGNED,
  enlargerLensID TINYINT UNSIGNED,
  filterID TINYINT UNSIGNED,
  headHeight TINYINT UNSIGNED DEFAULT NULL,
  filmSize ENUM ('35mm', '120', 'Sheet'),
  lux TINYINT UNSIGNED NOT NULL,
  fstop DECIMAL (3,1) UNSIGNED NOT NULL,
  exposureTime SMALLINT DEFAULT NULL,
  gammaStepA TINYINT UNSIGNED DEFAULT NULL,
  gammaStepB TINYINT UNSIGNED DEFAULT NULL,
  gamma DECIMAL(3,2) UNSIGNED DEFAULT NULL,
  expLog DECIMAL (3,2) UNSIGNED AS (LOG10(lux * exposureTime * 1000)) VIRTUAL,
  PRIMARY KEY (userID, filmTestID),
  CONSTRAINT FilmTests_DevRecipes_fk FOREIGN KEY (userID, devRecipeID) REFERENCES DevRecipes (userID, devRecipeID) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT FilmTests_FilmTypes_fk FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT FilmTests_Enlargers_fk FOREIGN KEY (userID, enlargerID) REFERENCES Enlargers (userID, enlargerID) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT FilmTests_EnlargerLenses_fk FOREIGN KEY (userID, enlargerLensID) REFERENCES EnlargerLenses (userID, enlargerLensID) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT FilmTests_Filters_fk FOREIGN KEY (userID, filterID) REFERENCES Filters (userID, filterID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE FilmTestSteps (
  userID INT UNSIGNED NOT NULL,
  filmTestID INT UNSIGNED NOT NULL,
  stepNumber TINYINT UNSIGNED NOT NULL,
  stepDensity DECIMAL(3,2) NOT NULL,
  stepFilmDensity DECIMAL(3,2) NOT NULL,
  PRIMARY KEY (userID, filmTestID, stepNumber),
  CONSTRAINT FilmTestSteps_FilmTests_fk FOREIGN KEY (userID, filmTestID) REFERENCES FilmTests (userID, filmTestID)
) ENGINE='InnoDB';

-- Tests
-- INSERT INTO DevRecipes VALUES (1, 1, 'XTOL-R', 'Black and White', 0, (60 * 8.5), 20, 'Water', 'Rotary', 'Test');
-- INSERT INTO FilmTests VALUES (1, 1, 1, 1, 1, 1, '20', '35mm', 12, 5.6, 2, NULL, NULL, NULL, NULL)

CREATE VIEW FilterStepsView AS
SELECT FilmTestSteps.userID, FilmTestSteps.filmTestID, stepNumber, stepDensity,
LOG10(lux * 1/exposureTime * 1000) - stepDensity AS LogE,
stepFilmDensity
FROM FilmTestSteps
JOIN FilmTests ON FilmTests.filmTestID = FilmTestSteps.filmTestID
    AND FilmTests.userID = FilmTestSteps.userID;
