CREATE TABLE PaperDevelopers(
    paperDeveloperID TINYINT UNSIGNED NOT NULL auto_increment PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    dilution TINYINT UNSIGNED NOT NULL,
    UNIQUE  name_dilution (name, dilution)
) ENGINE='InnoDB';

INSERT INTO PaperDevelopers VALUES (1, 'Ilford Multigrade', '9');
INSERT INTO PaperDevelopers VALUES (2, 'Ilford Multigrade', '14');

ALTER TABLE Prints ADD COLUMN paperDeveloperID TINYINT UNSIGNED DEFAULT NULL AFTER paperID,
ADD CONSTRAINT Prints_PaperDevelopers_fk FOREIGN KEY (paperDeveloperID) REFERENCES PaperDevelopers (paperDeveloperID);
