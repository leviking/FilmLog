CREATE TABLE Migrations (
  name varchar(64) NOT NULL PRIMARY KEY
) ENGINE='InnoDB';

CREATE TABLE Users (
    userID INT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    username varchar(64) NOT NULL,
    email varchar(255) DEFAULT NULL,
    password varbinary(128) NOT NULL,
    createdOn TIMESTAMP DEFAULT 0,
    lastLogin TIMESTAMP DEFAULT 0,
    UNIQUE email_uq (email),
    UNIQUE username_uq (username)
) ENGINE='InnoDB';

CREATE TABLE UserPreferences (
    userID INT UNSIGNED NOT NULL PRIMARY KEY,
    autoUpdateFilmStock ENUM('Yes', 'No') DEFAULT 'Yes',
    CONSTRAINT userprefs_userID_fk FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE UsersUnverified(
    userUnverifiedID INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username varchar(64) NOT NULL,
    email varchar(255) NOT NULL,
    password varbinary(128) NOT NULL,
    registrationCode varchar(255) NOT NULL,
    UNIQUE KEY `email_uq` (`email`),
    UNIQUE KEY `username_uq` (`username`)
) ENGINE='InnoDB';

CREATE TABLE Files(
    fileID INT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    PRIMARY KEY (fileID, userID),
    CONSTRAINT Files_Users_fk FOREIGN KEY (userID) REFERENCES Users (userID)
) ENGINE='InnoDB';

CREATE TABLE GlobalFilmBrands(
    filmBrandID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    brand varchar(64) NOT NULL,
    UNIQUE brand_uq (brand)
) ENGINE='InnoDB';

CREATE TABLE GlobalFilmTypes (
    filmTypeID SMALLINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    filmBrandID TINYINT UNSIGNED NOT NULL,
    name varchar(64) NOT NULL,
    iso smallint unsigned,
    kind enum('Color Negative','Black & White Negative','Color Slide','Black & White Slide', 'Motion Picture Color Negative') DEFAULT NULL,
    UNIQUE brand_name_iso_uq (filmBrandID, name, iso),
    KEY filmtypes_filmBrandID_fk (filmBrandID),
    CONSTRAINT filmtypes_filmBrandID FOREIGN KEY (filmBrandID) REFERENCES GlobalFilmBrands (filmBrandID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE FilmTypes (
    userID INT UNSIGNED NOT NULL,
    filmTypeID SMALLINT UNSIGNED NOT NULL,
    name varchar(64) NOT NULL,
    iso smallint unsigned,
    kind enum('Color Negative','Black & White Negative','Color Slide','Black & White Slide', 'Motion Picture Color Negative') DEFAULT NULL,
    displayColor INT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (userID, filmTypeID),
    UNIQUE KEY user_name_iso_uq (userID, name, iso),
    CONSTRAINT FilmTypes_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE FilmSizes (
    filmSizeID TINYINT UNSIGNED NOT NULL PRIMARY KEY,
    size VARCHAR(32),
    type ENUM('Miniature', 'Small', 'Medium', 'Large', 'Ultra-Large') NOT NULL,
    format ENUM('Roll', 'Sheet')
) ENGINE='InnoDB';

CREATE TABLE Cameras (
    userID INT UNSIGNED NOT NULL,
    cameraID SMALLINT UNSIGNED NOT NULL,
    loadedFilmTypeID SMALLINT UNSIGNED DEFAULT NULL,
    filmSize ENUM('35mm', '120', '220', '4x5', '5x7', '8x10') NOT NULL,
    integratedShutter ENUM('Yes', 'No') DEFAULT 'No',
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    name varchar(64) NOT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (userID, cameraID),
    UNIQUE user_name_eq (userID, name),
    CONSTRAINT Cameras_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT Cameras_FilmTypes_fk FOREIGN KEY (userID, loadedFilmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Lenses(
    userID INT UNSIGNED NOT NULL,
    lensID SMALLINT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    shutter ENUM ('Yes', 'No') DEFAULT 'No',
    PRIMARY KEY(userID, lensID),
    UNIQUE user_name_uq (userID, name),
    CONSTRAINT Lenses_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE CameraLenses(
    userID INT UNSIGNED NOT NULL,
    cameraID SMALLINT UNSIGNED NOT NULL,
    lensID SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (userID, cameraID, lensID),
    CONSTRAINT CameraLenses_Cameras FOREIGN KEY (userID, cameraID) REFERENCES Cameras (userID, cameraID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT CameraLenses_Lenses FOREIGN KEY (userID, lensID) REFERENCES Lenses (userID, lensID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE LensShutterSpeeds(
    userID INT UNSIGNED NOT NULL,
    lensID SMALLINT UNSIGNED NOT NULL,
    speed SMALLINT UNSIGNED NOT NULL,
    measuredSpeed SMALLINT AS (1/(measuredSpeedMicroseconds / 1000000)) VIRTUAL,
    idealSpeedMicroseconds INT UNSIGNED AS ((1/speed) * 1000000) VIRTUAL,
    measuredSpeedMicroseconds INT UNSIGNED NOT NULL,
    differenceStops FLOAT GENERATED ALWAYS AS ((ROUND(LOG2((1 / speed * 1000000) / measuredSpeedMicroseconds),2)) * -1),
    PRIMARY KEY (userID, lensID, speed),
    CONSTRAINT LensShutterSpeeds_Lenses FOREIGN KEY (userID, lensID) REFERENCES Lenses
        (userID, lensID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE CameraShutterSpeeds(
    userID INT UNSIGNED NOT NULL,
    cameraID SMALLINT UNSIGNED NOT NULL,
    speed SMALLINT UNSIGNED NOT NULL,
    measuredSpeed SMALLINT AS (1/(measuredSpeedMicroseconds / 1000000)) VIRTUAL,
    idealSpeedMicroseconds INT UNSIGNED AS ((1/speed) * 1000000) VIRTUAL,
    measuredSpeedMicroseconds INT UNSIGNED NOT NULL,
    differenceStops FLOAT GENERATED ALWAYS AS ((ROUND(LOG2((1 / speed * 1000000) / measuredSpeedMicroseconds),2)) * -1),
    PRIMARY KEY (userID, cameraID, speed),
    CONSTRAINT CameraShutterSpeeds_Cameras FOREIGN KEY (userID, cameraID) REFERENCES Cameras
        (userID, cameraID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE FilmStock(
    userID INT UNSIGNED NOT NULL,
    filmTypeID SMALLINT UNSIGNED NOT NULL,
    filmSizeID TINYINT UNSIGNED NOT NULL,
    qty SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (userID, filmTypeID, filmSizeID),
    KEY filmtypeID_fk (filmTypeID),
    CONSTRAINT FilmStock_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FilmStock_FilmTypes_fk FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT FilmStock_filmSizeID_fk FOREIGN KEY (filmSizeID) REFERENCES FilmSizes (filmSizeID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Binders(
    userID INT UNSIGNED NOT NULL,
    binderID SMALLINT UNSIGNED NOT NULL,
    name varchar(64) NOT NULL,
    projectCount TINYINT UNSIGNED NOT NULL DEFAULT 0,
    createdOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY(userID, binderID),
    UNIQUE KEY user_name_uq (userID, name),
    CONSTRAINT Binders_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Projects(
    userID INT UNSIGNED NOT NULL,
    projectID SMALLINT UNSIGNED NOT NULL,
    binderID SMALLINT UNSIGNED NOT NULL,
    filmCount SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    createdOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name varchar(64) NOT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY(userID, projectID),
    UNIQUE KEY binder_name_uq (userID, binderID, name),
    CONSTRAINT Projects_Binders_fk FOREIGN KEY (userID, binderID) REFERENCES Binders (userID, binderID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Films (
    userID INT UNSIGNED NOT NULL,
    filmID INT UNSIGNED NOT NULL,
    projectID SMALLINT UNSIGNED NOT NULL,
    cameraID SMALLINT UNSIGNED DEFAULT NULL,
    lensID SMALLINT UNSIGNED DEFAULT NULL,
    filmTypeID SMALLINT UNSIGNED DEFAULT NULL,
    filmSizeID TINYINT UNSIGNED NOT NULL,
    iso SMALLINT UNSIGNED DEFAULT NULL,
    fileDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    loaded TIMESTAMP NULL,
    unloaded TIMESTAMP NULL,
    developed TIMESTAMP NULL,
    exposures TINYINT UNSIGNED NOT NULL DEFAULT 0,
    fileNo varchar(32) NOT NULL,
    title varchar(64) NOT NULL,
    development varchar(255) DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (userID, filmID),
    UNIQUE KEY (userID, projectID, fileNo),
    UNIQUE KEY (userID, projectID, title),
    KEY films_projectID_fk (projectID),
    KEY films_cameraID_fk (cameraID),
    KEY films_filmTypeID_fk (filmTypeID),
    KEY lensID_fk (lensID),
    CONSTRAINT Films_projectID_fk FOREIGN KEY (userID, projectID) REFERENCES Projects (userID, projectID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Films_Cameras_fk FOREIGN KEY (userID, cameraID) REFERENCES Cameras (userID, cameraID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Films_FilmTypes_fk FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Films_filmSizeID_fk FOREIGN KEY (filmSizeID) REFERENCES FilmSizes (filmSizeID) ON UPDATE CASCADE,
    CONSTRAINT Films_Lenses_fk FOREIGN KEY (userID, lensID) REFERENCES Lenses (userID, lensID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Holders (
    userID INT UNSIGNED NOT NULL,
    holderID SMALLINT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    size ENUM('4x5', '5x7', '8x10', '11x14') DEFAULT '4x5' NOT NULL,
    status ENUM ('Active', 'Retired') DEFAULT 'Active' NOT NULL,
    loaded DATE DEFAULT NULL,
    exposed DATE DEFAULT NULL,
    unloaded DATE DEFAULT NULL,
    filmTypeID SMALLINT UNSIGNED DEFAULT NULL,
    iso SMALLINT UNSIGNED DEFAULT NULL,
    compensation TINYINT DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (userID, holderID),
    UNIQUE user_name_eq (userID, name),
    CONSTRAINT Holders_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT Holders_FilmTypes_fk FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Both Roll and Sheet
CREATE TABLE Exposures(
    userID INT UNSIGNED NOT NULL,
    filmID INT UNSIGNED NOT NULL,
    exposureNumber TINYINT UNSIGNED NOT NULL,
    filmTypeID SMALLINT UNSIGNED DEFAULT NULL,
    filmSizeID TINYINT UNSIGNED DEFAULT NULL,
    lensID SMALLINT UNSIGNED DEFAULT NULL,
    holderID SMALLINT UNSIGNED DEFAULT NULL,
    iso SMALLINT UNSIGNED DEFAULT NULL,
    shutter SMALLINT DEFAULT NULL,
    aperture DECIMAL(4,1) UNSIGNED DEFAULT NULL,
    flash ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    metering ENUM('Incident', 'Reflective') DEFAULT NULL,
    stability ENUM('Handheld', 'Tripod') DEFAULT NULL,
    subject VARCHAR(128) DEFAULT NULL,
    development VARCHAR(255) DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (userID, filmID, exposureNumber),
    KEY filmTypeID_idx (filmTypeID),
    KEY lensID_idx (lensID),
    KEY userID_idx (userID),
    CONSTRAINT Exposures_FilmTypes_fk FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Exposures_Films_fk FOREIGN KEY (userID, filmID) REFERENCES Films (userID, filmID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Exposures_Lenses_fk FOREIGN KEY (userID, lensID) REFERENCES Lenses (userID, lensID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Exposures_filmSizeID_fk FOREIGN KEY (filmSizeID) REFERENCES FilmSizes (filmSizeID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Exposure_Holders_fk FOREIGN KEY (userID, holderID) REFERENCES Holders (userID, holderID) ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Filters(
    userID INT UNSIGNED NOT NULL,
    filterID TINYINT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    code VARCHAR(8) NOT NULL,
    factor DECIMAL(4, 1) NOT NULL,
    ev DECIMAL(3,1) NOT NULL,
    PRIMARY KEY (userID, filterID),
    UNIQUE user_name (userID, name),
    UNIQUE user_code (userID, code),
    CONSTRAINT Filters_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE ExposureFilters(
    userID INT UNSIGNED NOT NULL,
    filmID INT UNSIGNED NOT NULL,
    exposureNumber TINYINT UNSIGNED NOT NULL,
    filterID TINYINT UNSIGNED NOT NULL,
    PRIMARY KEY (userID, filmID, exposureNumber, filterID),
    CONSTRAINT ExposureFilters_Exposures_fk FOREIGN KEY (userID, filmID, exposureNumber) REFERENCES Exposures (userID, filmID, exposureNumber) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ExposureFilters_Filters_fk FOREIGN KEY (userID, filterID) REFERENCES Filters (userID, filterID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

-- Darkroom
CREATE TABLE PaperDevelopers(
    paperDeveloperID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    dilution TINYINT UNSIGNED NOT NULL,
    UNIQUE  name_dilution (name, dilution)
) ENGINE='InnoDB';

CREATE TABLE Papers(
    userID INT UNSIGNED NOT NULL,
    paperID TINYINT UNSIGNED NOT NULL,
    type ENUM('Resin Coated', 'Fibre Base', 'Cotton Rag'),
    grade ENUM('Multi', 'Fixed'),
    surface ENUM('Glossy', 'Pearl', 'Satin', 'Semi-Matt', 'Matt'),
    tone ENUM('Cool', 'Neutral', 'Warm'),
    numPrints SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    numContactSheets SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    name varchar(64),
    PRIMARY KEY (userID, paperID),
    UNIQUE user_name (userID, name),
    CONSTRAINT papers_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE PaperFilters(
    paperFilterID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    name varchar(12) NOT NULL
) ENGINE='InnoDB';

CREATE TABLE EnlargerLenses(
    enlargerLensID TINYINT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    PRIMARY KEY (enlargerLensID, userID),
    UNIQUE KEY user_name_uq (userID, name),
    KEY userID_idx (userID),
    CONSTRAINT EnlargerLenses_Users_fk FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE Enlargers(
    userID INT UNSIGNED NOT NULL,
    enlargerID TINYINT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    type ENUM('Condenser', 'Diffuser'),
    lightsource ENUM('LED', 'Incandescent', 'Cold Light'),
    wattage SMALLINT UNSIGNED,
    temperature SMALLINT UNSIGNED,
    notes TEXT,
    PRIMARY KEY (userID, enlargerID),
    UNIQUE KEY user_name_uq (userID, name),
    CONSTRAINT Enlargers_Users_fk FOREIGN KEY (userID) REFERENCES Users (userID) ON UPDATE CASCADE
);

CREATE TABLE ContactSheets(
    filmID INT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    fileID INT UNSIGNED DEFAULT NULL,
    paperID TINYINT UNSIGNED DEFAULT NULL,
    paperFilterID TINYINT UNSIGNED DEFAULT NULL,
    enlargerLensID TINYINT UNSIGNED DEFAULT NULL,
    enlargerID TINYINT UNSIGNED DEFAULT NULL,
    aperture decimal(3,1) DEFAULT NULL,
    headHeight TINYINT UNSIGNED,
    exposureTime SMALLINT UNSIGNED NOT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (filmID, userID),
    CONSTRAINT ContactSheets_Files_fk FOREIGN KEY (userID, fileID) REFERENCES Files (userID, fileID),
    CONSTRAINT ContactSheets_EnlargerLenses_fk FOREIGN KEY (userID, enlargerLensID) REFERENCES EnlargerLenses (userID, enlargerLensID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ContactSheets_Enlargers_fk FOREIGN KEY (userID, enlargerID) REFERENCES Enlargers (userID, enlargerID),
    CONSTRAINT ContactSheets_Papers_fk FOREIGN KEY (userID, paperID) REFERENCES Papers (userID, paperID)
) ENGINE='InnoDB';

CREATE TABLE Prints (
    printID INT UNSIGNED NOT NULL,
    filmID INT UNSIGNED NOT NULL,
    exposureNumber TINYINT UNSIGNED NOT NULL,
    userID INT UNSIGNED NOT NULL,
    paperID TINYINT UNSIGNED DEFAULT NULL,
    paperDeveloperID TINYINT UNSIGNED DEFAULT NULL,
    paperFilterID TINYINT UNSIGNED DEFAULT NULL,
    enlargerLensID TINYINT UNSIGNED DEFAULT NULL,
    enlargerID TINYINT UNSIGNED DEFAULT NULL,
    fileID INT UNSIGNED DEFAULT NULL,
    aperture decimal(3,1) DEFAULT NULL,
    ndFilter decimal(3,1) DEFAULT NULL,
    headHeight TINYINT UNSIGNED DEFAULT NULL,
    printType ENUM('Enlargement', 'Contact') NOT NULL,
    size ENUM ('4x5', '4x6', '5x7', '8x10', '11x14', 'Other') NOT NULL,
    exposureTime SMALLINT UNSIGNED,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (userID, printID),
    KEY paperID_fk (paperID),
    KEY paperFilterID_fk (paperFilterID),
    KEY film_exposure_fk (filmID, exposureNumber),
    KEY user_film_exposure (userID, filmID, exposureNumber),
    CONSTRAINT Prints_Papers_fk FOREIGN KEY (userID, paperID) REFERENCES Papers (userID, paperID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT prints_paperFilterID_fk FOREIGN KEY (paperFilterID) REFERENCES PaperFilters (paperFilterID) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT Prints_Exposures_fk FOREIGN KEY (userID, filmID, exposureNumber) REFERENCES Exposures (userID, filmID, exposureNumber),
    CONSTRAINT Prints_Files_fk FOREIGN KEY (userID, fileID) REFERENCES Files (userID, fileID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT Prints_EnlargerLenses_fk FOREIGN KEY (userID, enlargerLensID) REFERENCES EnlargerLenses (userID, enlargerLensID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT Prints_Enlargers_fk FOREIGN KEY (userID, enlargerID) REFERENCES Enlargers (userID, enlargerID),
    CONSTRAINT Prints_PaperDevelopers_fk FOREIGN KEY (paperDeveloperID) REFERENCES PaperDevelopers (paperDeveloperID)
) ENGINE='InnoDB';

CREATE TABLE MaxBlackTests(
  userID INT UNSIGNED NOT NULL,
  paperID TINYINT UNSIGNED,
  filmTypeID SMALLINT UNSIGNED,
  enlargerID TINYINT UNSIGNED DEFAULT NULL,
  enlargerLensID TINYINT UNSIGNED DEFAULT NULL,
  heatHeight SMALLINT UNSIGNED DEFAULT NULL,
  aperture DECIMAL(4,1) NOT NULL,
  size ENUM('4x5','4x6','5x7','8x10','11x14','Other') NOT NULL,
  exposureTime SMALLINT UNSIGNED NOT NULL,
  notes TEXT,
  PRIMARY KEY (userID, paperID, filmTypeID),
  CONSTRAINT mbt_users FOREIGN KEY (userID) REFERENCES Users (userID),
  CONSTRAINT mbt_papers FOREIGN KEY (userID, paperID) REFERENCES Papers (userID, paperID),
  CONSTRAINT mbt_filmTypes FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID),
  CONSTRAINT mbt_enlargers FOREIGN KEY (userID, enlargerID) REFERENCES Enlargers (userID, enlargerID),
  CONSTRAINT mbt_enlargerLenses FOREIGN KEY (userID, enlargerLensID) REFERENCES EnlargerLenses (userID, enlargerLensID)
) ENGINE='InnoDB';

CREATE TABLE Developers (
  userID INT UNSIGNED NOT NULL,
  developerID TINYINT UNSIGNED NOT NULL,
  name VARCHAR(64) NOT NULL,
  mixedOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  type ENUM('Black & White', 'C-41', 'E-6', 'ECN2') NOT NULL DEFAULT 'Black & White',
  kind ENUM('One-Shot', 'Multi-User', 'Replenishment') DEFAULT 'One-Shot',
  state ENUM('Active', 'Retired') DEFAULT 'Active',
  capacity SMALLINT UNSIGNED NOT NULL,
  notes TEXT DEFAULT NULL,
  PRIMARY KEY (userID, developerID),
  UNIQUE KEY (userID, name),
  CONSTRAINT Developers_userID_fk FOREIGN KEY (userID)
    REFERENCES Users (userID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE DeveloperLogs(
    userID INT UNSIGNED NOT NULL,
    developerLogID INT UNSIGNED NOT NULL,
    developerID TINYINT UNSIGNED NOT NULL,
    loggedOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mlReplaced SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    mlUsed SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    temperature DECIMAL(4,1) DEFAULT NULL,
    devTime INT UNSIGNED DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    PRIMARY KEY (userID, developerLogID),
    KEY loggedOn_idx (loggedOn),
    CONSTRAINT DeveloperLogs_Developers_fk FOREIGN KEY (userID, developerID)
        REFERENCES Developers (userID, developerID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE DeveloperLogFilms(
  userID INT UNSIGNED NOT NULL,
  developerLogFilmID INT UNSIGNED NOT NULL,
  developerLogID INT UNSIGNED NOT NULL,
  filmSizeID TINYINT UNSIGNED NOT NULL,
  filmTypeID SMALLINT UNSIGNED DEFAULT NULL,
  qty TINYINT UNSIGNED NOT NULL,
  compensation TINYINT DEFAULT NULL DEFAULT 0,
  PRIMARY KEY (userID, developerLogFilmID),
  UNIQUE KEY user_developerlog_size_type_uq (userID, developerLogID, filmSizeID, filmTypeID),
  CONSTRAINT DeveloperLogFilms_DeveloperLogs_fk FOREIGN KEY (userID, developerLogID)
      REFERENCES DeveloperLogs (userID, developerLogID) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT DeveloperLogFilms_FilmSizes_fk FOREIGN KEY (filmSizeID)
    REFERENCES FilmSizes (filmSizeID) ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE StepTablets (
  userID INT UNSIGNED NOT NULL,
  stepTabletID TINYINT UNSIGNED NOT NULL,
  name VARCHAR(64) NOT NULL,
  createdOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (userID, stepTabletID),
  UNIQUE KEY (userID, name),
  CONSTRAINT StepTablets_Users_fk FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE StepTabletSteps (
  userID INT UNSIGNED NOT NULL,
  stepTabletID TINYINT UNSIGNED NOT NULL,
  stepNumber TINYINT UNSIGNED NOT NULL,
  stepDensity DECIMAL(3,2) NOT NULL,
  PRIMARY KEY (userID, stepTabletID, stepNumber),
  CONSTRAINT StepTabletSteps_StepTablets_fk FOREIGN KEY (userID, stepTabletID) REFERENCES StepTablets (userID, stepTabletID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE FilmTests (
  userID INT UNSIGNED NOT NULL,
  filmTestID INT UNSIGNED NOT NULL,
  devRecipeID SMALLINT UNSIGNED NOT NULL,
  filmTypeID SMALLINT UNSIGNED NOT NULL,
  stepTabletID TINYINT UNSIGNED NOT NULL,
  enlargerID TINYINT UNSIGNED,
  enlargerLensID TINYINT UNSIGNED,
  filterID TINYINT UNSIGNED,
  testedOn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  headHeight SMALLINT UNSIGNED DEFAULT NULL,
  filmSize ENUM ('35mm', '120', 'Sheet'),
  lux TINYINT UNSIGNED NOT NULL,
  fstop DECIMAL (3,1) UNSIGNED NOT NULL,
  exposureTime DECIMAL(4,2) UNSIGNED NOT NULL,
  devTime SMALLINT UNSIGNED NOT NULL,
  devTemperature DECIMAL(3,1) UNSIGNED NOT NULL,
  prebath ENUM('No','Water') NOT NULL DEFAULT 'No',
  stop ENUM('Stop Bath','Water') NOT NULL DEFAULT 'Stop Bath',
  agitation ENUM('Rotary','Hand-Inversions','Dip and Dunk','Tray') NOT NULL DEFAULT 'Hand-Inversions',
  rotaryRPM TINYINT UNSIGNED DEFAULT NULL,
  baseFog DECIMAL (3,2) UNSIGNED DEFAULT NULL,
  dMax DECIMAL(3,2) UNSIGNED DEFAULT NULL;
  gamma DECIMAL(3,2) UNSIGNED DEFAULT NULL,
  contrastIndex DECIMAL(3,2) UNSIGNED DEFAULT NULL,
  kodakISO SMALLINT UNSIGNED DEFAULT NULL,
  expLog DECIMAL (3,2) UNSIGNED AS (ROUND(LOG10(lux * exposureTime * 1000), 2)) VIRTUAL,
  graph ENUM('Yes', 'No') DEFAULT 'No',
  developer VARCHAR(32) NOT NULL,
  notes TEXT DEFAULT NULL,
  PRIMARY KEY (userID, filmTestID),
  CONSTRAINT FilmTests_DevRecipes_fk FOREIGN KEY (userID, devRecipeID) REFERENCES DevRecipes (userID, devRecipeID) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT FilmTests_StepTablets_fk FOREIGN KEY (userID, stepTabletID) REFERENCES StepTablets (userID, stepTabletID) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT FilmTests_FilmTypes_fk FOREIGN KEY (userID, filmTypeID) REFERENCES FilmTypes (userID, filmTypeID) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT FilmTests_Enlargers_fk FOREIGN KEY (userID, enlargerID) REFERENCES Enlargers (userID, enlargerID) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT FilmTests_EnlargerLenses_fk FOREIGN KEY (userID, enlargerLensID) REFERENCES EnlargerLenses (userID, enlargerLensID) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT FilmTests_Filters_fk FOREIGN KEY (userID, filterID) REFERENCES Filters (userID, filterID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE TABLE FilmTestSteps (
  userID INT UNSIGNED NOT NULL,
  filmTestID INT UNSIGNED NOT NULL,
  stepNumber TINYINT UNSIGNED NOT NULL,
  filmDensity DECIMAL(3,2) NOT NULL,
  PRIMARY KEY (userID, filmTestID, stepNumber),
  CONSTRAINT FilmTestSteps_FilmTests_fk FOREIGN KEY (userID, filmTestID) REFERENCES FilmTests (userID, filmTestID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE='InnoDB';

CREATE VIEW FilmTestsView AS
SELECT FilmTests.filmTestID, FilmTypes.name AS filmName, FilmTypes.iso AS filmISO,
filmSize, developer, SEC_TO_TIME(devTime) AS devTime, Filters.code AS filter,
lux, fstop,
gamma, contrastIndex, kodakISO
FROM FilmTests
JOIN FilmTypes ON FilmTypes.userID = FilmTests.userID
    AND FilmTypes.filmTypeID = FilmTests.filmTypeID
JOIN Filters ON Filters.userID = FilmTests.userID
    AND Filters.filterID = FilmTests.filterID
ORDER BY filmName, filmISO, devTime;

CREATE VIEW FilmTestStepsView AS
SELECT FilmTestSteps.userID, FilmTestSteps.filmTestID, FilmTestSteps.stepNumber, stepDensity,
ROUND(LOG10(lux * exposureTime * 1000) - stepDensity, 2) AS logE, filmDensity
FROM FilmTestSteps
JOIN FilmTests ON FilmTests.filmTestID = FilmTestSteps.filmTestID
    AND FilmTests.userID = FilmTestSteps.userID
JOIN StepTablets ON StepTablets.stepTabletID = FilmTests.stepTabletID
    AND StepTablets.userID = FilmTests.userID
JOIN StepTabletSteps ON StepTabletSteps.stepTabletID = StepTablets.stepTabletID
    AND StepTabletSteps.userID = StepTablets.userID
    AND StepTabletSteps.stepNumber = FilmTestSteps.stepNumber;

-- Functions
DROP FUNCTION IF EXISTS SECONDS_TO_DURATION;
DELIMITER //
CREATE FUNCTION SECONDS_TO_DURATION (inSeconds SMALLINT) RETURNS VARCHAR(8) DETERMINISTIC
BEGIN
    DECLARE minutes TINYINT UNSIGNED;
    DECLARE seconds TINYINT UNSIGNED;
    SELECT ROUND(FLOOR(inSeconds / 60)) INTO minutes;
    SELECT inSeconds % 60 INTO seconds;
    IF minutes < 10
    THEN
        SELECT CONCAT('0', minutes) INTO minutes;
    END IF;
    IF seconds < 10
    THEN
        SELECT CONCAT('0', seconds) INTO seconds;
    END IF;
    RETURN CONCAT(IF(minutes < 10,CONCAT('0', minutes),minutes), ':',
        IF(seconds < 10,CONCAT('0', seconds), seconds));
END
//
DELIMITER ;

-- Triggers
DELIMITER //
CREATE TRIGGER ProjectCountIncrement
    BEFORE INSERT ON Projects
        FOR EACH ROW
        BEGIN
            UPDATE Binders SET projectCount = projectCount + 1
            WHERE binderID = NEW.binderID
            AND userID = NEW.userID;
        END;
//
CREATE TRIGGER ProjectCountDecrement
    BEFORE DELETE ON Projects
        FOR EACH ROW
        BEGIN
            UPDATE Binders SET projectCount = projectCount - 1
            WHERE binderID = OLD.binderID
            AND userID = OLD.userID;
        END;
//

CREATE TRIGGER FilmCountIncrement
    BEFORE INSERT ON Films
        FOR EACH ROW
        BEGIN
            UPDATE Projects SET filmCount = filmCount + 1
            WHERE projectID = NEW.projectID
            AND userID = NEW.userID;
        END;
//

CREATE TRIGGER FilmCountDecrement
    BEFORE DELETE ON Films
        FOR EACH ROW
        BEGIN
            UPDATE Projects SET filmCount = filmCount - 1
            WHERE projectID = OLD.projectID
            AND userID = OLD.userID;
        END;
//

CREATE TRIGGER ExposureCountIncrement
    BEFORE INSERT ON Exposures
        FOR EACH ROW
        BEGIN
            UPDATE Films SET exposures = exposures + 1
            WHERE filmID = NEW.filmID
            AND userID = NEW.userID;
        END;
//

CREATE TRIGGER ExposureCountDecrement
    BEFORE DELETE ON Exposures
        FOR EACH ROW
        BEGIN
            UPDATE Films SET exposures = exposures - 1
            WHERE filmID = OLD.filmID
            AND userID = OLD.userID;
        END;
//

CREATE TRIGGER PrintsCountIncrement
    BEFORE INSERT ON Prints
        FOR EACH ROW
        BEGIN
            UPDATE Papers SET numPrints = numPrints + 1
            WHERE paperID = NEW.paperID
            AND userID = NEW.userID;
        END;
//

CREATE TRIGGER PrintsCountDecrement
    BEFORE DELETE ON Prints
        FOR EACH ROW
        BEGIN
            UPDATE Papers SET numPrints = numPrints - 1
            WHERE paperID = OLD.paperID
            AND userID = OLD.userID;
        END;
//

CREATE TRIGGER ContactSheetsCountIncrement
    BEFORE INSERT ON ContactSheets
        FOR EACH ROW
        BEGIN
            UPDATE Papers SET numContactSheets = numContactSheets + 1
            WHERE paperID = NEW.paperID
            AND userID = NEW.userID;
        END;
//

CREATE TRIGGER ContactSheetsCountDecrement
    BEFORE DELETE ON ContactSheets
        FOR EACH ROW
        BEGIN
            UPDATE Papers SET numContactSheets = numContactSheets - 1
            WHERE paperID = OLD.paperID
            AND userID = OLD.userID;
        END;
//

CREATE TRIGGER CreateDefaultUserPreferences
    AFTER INSERT ON Users
        FOR EACH ROW
        BEGIN
            INSERT INTO UserPreferences (userID) VALUES (NEW.userID);
        END;
//

DELIMITER ;
