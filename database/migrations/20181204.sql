-- Dropping Recipes as a half-baked feature made it into master, oops
DROP TABLE IF EXISTS Recipes;

DROP TABLE IF EXISTS DeveloperLogFilms;
DROP TABLE IF EXISTS DeveloperLogs;
DROP TABLE IF EXISTS Developers;

CREATE TABLE Developers (
  userID INT UNSIGNED NOT NULL,
  developerID TINYINT UNSIGNED NOT NULL,
  name VARCHAR(64) NOT NULL,
  mixedOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  replenishment ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
  state ENUM('Active', 'Retired') DEFAULT 'Active',
  notes TEXT DEFAULT NULL,
  PRIMARY KEY (userID, developerID),
  UNIQUE KEY (name),
  CONSTRAINT Developers_userID_fk FOREIGN KEY (userID)
    REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE DeveloperLogs(
    userID INT UNSIGNED NOT NULL,
    developerLogID INT UNSIGNED NOT NULL,
    developerID TINYINT UNSIGNED NOT NULL,
    loggedOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mlReplaced SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    temperature DECIMAL(4,1) DEFAULT NULL,
    devTime INT UNSIGNED DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (userID, developerLogID),
    CONSTRAINT DeveloperLogs_Developers_fk FOREIGN KEY (userID, developerID)
        REFERENCES Developers (userID, developerID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE DeveloperLogFilms(
  userID INT UNSIGNED NOT NULL,
  developerLogFilmID INT UNSIGNED NOT NULL,
  developerLogID INT UNSIGNED NOT NULL,
  filmSize ENUM('35mm', '120', '220', '4x5', '8x10') NOT NULL,
  filmTypeID SMALLINT UNSIGNED DEFAULT NULL,
  qty TINYINT UNSIGNED NOT NULL,
  compensation TINYINT NOT NULL DEFAULT 0,
  PRIMARY KEY (userID, developerLogFilmID),
  CONSTRAINT DeveloperLogFilms_DeveloperLogs_fk FOREIGN KEY (userID, developerLogID)
      REFERENCES DeveloperLogs (userID, developerLogID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

 
