SET FOREIGN_KEY_CHECKS = 0;
RENAME TABLE Papers TO PapersOld;

CREATE TABLE Papers(
    userID INT UNSIGNED NOT NULL,
    paperID TINYINT UNSIGNED NOT NULL,
    type ENUM('Resin Coated', 'Fibre Base', 'Cotton Rag'),
    grade ENUM('Multi', 'Fixed'),
    surface ENUM('Glossy', 'Pearl', 'Satin', 'Semi-Matt', 'Matt'),
    tone ENUM('Cool', 'Neutral', 'Warm'),
    name varchar(64),
    PRIMARY KEY (userID, paperID),
    CONSTRAINT papers_userID FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE='InnoDB';

INSERT INTO Papers
  SELECT 1, paperID, type, grade, surface, tone, CONCAT(PaperBrands.name, ' ', PapersOld.name)
    FROM PapersOld
    JOIN PaperBrands ON PaperBrands.paperBrandID = PapersOld.paperBrandID;
COMMIT;

DROP TABLE PaperBrands;
DROP TABLE PapersOld;

ALTER TABLE ContactSheets
  ADD CONSTRAINT ContactSheets_Papers_fk FOREIGN KEY (userID, paperID) REFERENCES Papers (userID, paperID);

ALTER TABLE Prints
  DROP FOREIGN KEY prints_paperID_fk,
  ADD CONSTRAINT Prints_Papers_fk FOREIGN KEY (userID, paperID) REFERENCES Papers (userID, paperID) ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE MaxBlackTests
  DROP FOREIGN KEY mbt_papers;
ALTER TABLE MaxBlackTests
  ADD CONSTRAINT mbt_papers FOREIGN KEY (userID, paperID) REFERENCES Papers (userID, paperID);

SET FOREIGN_KEY_CHECKS = 1;
