SET foreign_key_checks=0;
ALTER TABLE EnlargerLenses ADD UNIQUE KEY user_name_uq (userID, name);
SET foreign_key_checks=1;
