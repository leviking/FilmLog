CREATE TABLE Enlargers(
    userID INT UNSIGNED NOT NULL,
    enlargerID TINYINT UNSIGNED NOT NULL,
    name VARCHAR(64) NOT NULL,
    type ENUM('Condenscer', 'Diffuser'),
    lightsource ENUM('LED', 'Incandescent'),
    wattage SMALLINT UNSIGNED,
    PRIMARY KEY (userID, enlargerID),
    UNIQUE KEY user_name_uq (userID, name),
    CONSTRAINT Enlargers_Users_fk FOREIGN KEY (userID) REFERENCES Users (userID) ON UPDATE CASCADE
);
