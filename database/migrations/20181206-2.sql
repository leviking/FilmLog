ALTER TABLE Developers
  ADD COLUMN capacity SMALLINT UNSIGNED NOT NULL AFTER state;

ALTER TABLE DeveloperLogs
  ADD COLUMN mlUsed SMALLINT UNSIGNED DEFAULT NULL AFTER mlReplaced,
  MODIFY COLUMN mlReplaced SMALLINT UNSIGNED DEFAULT NULL;

ALTER TABLE DeveloperLogFilms
  DROP COLUMN filmSize,
  ADD COLUMN filmSizeID TINYINT UNSIGNED NOT NULL AFTER developerLogID;

UPDATE DeveloperLogFilms SET filmSizeID = 1;

ALTER TABLE DeveloperLogFilms
  ADD CONSTRAINT DeveloperLogFilms_FilmSizes_fk FOREIGN KEY (filmSizeID)
    REFERENCES FilmSizes (filmSizeID) ON UPDATE CASCADE;

ALTER TABLE DeveloperLogFilms
  MODIFY COLUMN compensation TINYINT DEFAULT NULL DEFAULT 0;

ALTER TABLE DeveloperLogFilms
  ADD UNIQUE KEY user_developerlog_size_type_uq (userID, developerLogID, filmSizeID, filmTypeID);

ALTER TABLE Developers
  DROP INDEX name;

ALTER TABLE Developers
  ADD UNIQUE KEY userID_name_uq (userID, name);
