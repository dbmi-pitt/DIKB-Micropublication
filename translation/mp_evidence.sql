START TRANSACTION;
SET standard_conforming_strings=off;
SET escape_string_warning=off;
SET CONSTRAINTS ALL DEFERRED;

-- Table: concept
-- DROP TABLE IF EXISTS concept;
create table concept 
   (concept_id INTEGER not null PRIMARY KEY, 
	concept_name text not null, 
	concept_level INTEGER, 
	concept_class text, 
	vocabulary_id INTEGER, 
	concept_code text, 
	valid_start_date date, 
	valid_end_date date default '31-dec-2099', 
	invalid_reason text
    )
WITH (
  OIDS=FALSE
);
ALTER TABLE concept
  OWNER TO postgres;

-- Table: mp_claim
-- DROP TABLE IF EXISTS mp_claim;
CREATE TABLE mp_claim
(
  claimId INTEGER not null PRIMARY KEY,
  concept_id INTEGER,
  label text,
  type text,
  uri text,
  subject text,
  object text,
  predicate text,
  npid INTEGER
);


-- Table: mp_data
-- DROP TABLE IF EXISTS mp_data;
CREATE TABLE mp_data
(
  dataId INTEGER not null PRIMARY KEY,
  concept_id INTEGER,
  type text,
  value_as_number INTEGER,
  value_as_string text,
  value_as_concept_id INTEGER
);

-- Table: mp_claim_data_relationship
-- DROP TABLE IF EXISTS mp_claim_data_relationship;
CREATE TABLE mp_claim_data_relationship
(
  Id serial PRIMARY KEY,
  concept_id INTEGER,
  role_as_concept_id INTEGER not null,
  claimId INTEGER,
  dataId INTEGER,
  FOREIGN KEY (claimId) REFERENCES mp_claim (claimId),
  FOREIGN KEY (dataId) REFERENCES mp_data (dataId)
);



-- Table: mp_method
-- DROP TABLE IF EXISTS mp_method;
CREATE TABLE mp_method
(
  methodId INTEGER PRIMARY KEY,
  concept_id INTEGER,
  type text
);


-- Table: mp_material
-- DROP TABLE IF EXISTS mp_material;
CREATE TABLE mp_material
(
  materialId INTEGER PRIMARY KEY,
  concept_id INTEGER,
  type text,
  value_as_number INTEGER,
  value_as_string text,
  value_as_concept_id INTEGER
);

-- Table: mp_statement
-- DROP TABLE IF EXISTS mp_statement;

CREATE TABLE mp_statement
(
  statementId INTEGER PRIMARY KEY,
  concept_id INTEGER,
  type text,
  value_as_number INTEGER,
  value_as_string text,
  value_as_concept_id INTEGER
);


-- Table: mp_claim_statement_relationship
-- DROP TABLE IF EXISTS mp_claim_statement_relationship;
CREATE TABLE mp_claim_statement_relationship
(
  Id serial PRIMARY KEY,
  concept_id INTEGER,
  role_as_concept_id INTEGER not null,
  claimId INTEGER,
  statementId INTEGER,
  FOREIGN KEY (claimId) REFERENCES mp_claim (claimId),
  FOREIGN KEY (statementId) REFERENCES mp_statement (statementId)
);


-- Table: mp_reference
--DROP TABLE IF EXISTS mp_reference;
CREATE TABLE mp_reference
(
  referenceId INTEGER PRIMARY KEY,
  concept_id INTEGER,
  type text,
  reference text,
  uri text
);

-- Table: mp_claim_reference_relationship
-- DROP TABLE IF EXISTS mp_claim_reference_relationship;
CREATE TABLE mp_claim_reference_relationship
(
  Id serial PRIMARY KEY,
  concept_id INTEGER,
  claimId INTEGER,
  referenceId INTEGER,
  FOREIGN KEY (claimId) REFERENCES mp_claim (claimId),
  FOREIGN KEY (referenceId) REFERENCES mp_reference (referenceId)
);


-- Table: mp_annotation
-- DROP TABLE IF EXISTS mp_annotation;
CREATE TABLE mp_annotation
(
  annotationId INTEGER PRIMARY KEY,
  concept_id INTEGER,
  type text,
  hasBodyDataId INTEGER,
  hasBodyMethodId INTEGER,
  hasBodyStatementId INTEGER,
  annotatedAt date,
  annotatedBy text,
  hasSource text,
  prefix text,
  exact text,
  postfix text
);

