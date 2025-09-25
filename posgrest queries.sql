use search;
CREATE EXTENSION vector;
SELECT * FROM pg_available_extensions WHERE name = 'vector';

create table document (
id serial primary key, 
content text, 
created_at timestamp default current_timestamp
);

select * from document;
select * from document_embedding;
drop table document;

create table document_embedding(
id SERIAL PRIMARY KEY,
doc_id INTEGER REFERENCES document(id),
embedding VECTOR(384) -- For MiniLM-L12-v2
);

truncate document_embedding;
truncate document;





