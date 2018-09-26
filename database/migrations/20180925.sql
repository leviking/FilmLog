CREATE TABLE Holders (
    userID INT UNSIGNED NOT NULL,
    holderID SMALLINT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    size ENUM('4x5', '5x7', '8x10', '11x14') DEFAULT '4x5' NOT NULL,
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
    CONSTRAINT Holders_filmTypeID FOREIGN KEY (filmTypeID) REFERENCES FilmTypes (filmTypeID) ON UPDATE CASCADE
) ENGINE=InnoDB;

ALTER TABLE Developers
ADD PRIMARY KEY (developerID),
ADD UNIQUE KEY (name);

ALTER TABLE Recipes
ADD CONSTRAINT Recipes_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON UPDATE CASCADE,
ADD CONSTRAINT Recipes_developerID FOREIGN KEY (developerID) REFERENCES Developers (developerID) ON UPDATE CASCADE;
