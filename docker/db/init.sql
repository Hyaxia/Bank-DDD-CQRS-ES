-- Table: public.aggregates

-- DROP TABLE public.aggregates;

CREATE TABLE public.aggregates
(
    uuid character varying(36) COLLATE pg_catalog."default" NOT NULL,
    version integer,
    CONSTRAINT aggregates_pkey PRIMARY KEY (uuid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.aggregates
    OWNER to postgres;


-- Table: public.events

-- DROP TABLE public.events;

CREATE TABLE public.events
(
    uuid character varying(36) COLLATE pg_catalog."default" NOT NULL,
    aggregate_uuid character varying(36) COLLATE pg_catalog."default",
    name character varying(50) COLLATE pg_catalog."default",
    data json,
    CONSTRAINT events_pkey PRIMARY KEY (uuid),
    CONSTRAINT events_aggregate_uuid_fkey FOREIGN KEY (aggregate_uuid)
        REFERENCES public.aggregates (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.events
    OWNER to postgres;


