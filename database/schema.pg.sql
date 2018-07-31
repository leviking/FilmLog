CREATE TABLE paper_brands(
    paper_brand_id smallserial NOT NULL PRIMARY KEY,
    name varchar(32) NOT NULL,
    UNIQUE (name)
);

