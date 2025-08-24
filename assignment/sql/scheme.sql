CREATE TABLE domain (
    id SERIAL PRIMARY KEY, --serial increment number
    fqdn VARCHAR(255) NOT NULL,
    regisered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), 
    unregisttered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),


    CONSTRAINT domain_fqdn_not_empty CHECK (LENGTH(TRIM(fqdn)) > 0),
    CONSTRAINT domain_registration_order CHECK (
        unregistered_at IS NULL OR unregistered_at > registered_at
    )
);
-- prevent overlapping fqdn
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE domain ADD CONSTRAINT no_overlap_for_fqdn
EXCLUDE USING gist (
    fqdn WITH =,
    tstzrange(registered_at, COALESCE(unregistered_at, 'infinity')) WITH &&
);

/*There is a bunch of flags which can be enabled on domain:
  - ``EXPIRED`` - domain is expired
  - ``OUTZONE`` - domain is not generated into zone (file)
  - ``DELETE_CANDIDATE`` - domain is marked to be deleted (unregistered) (e.g. by some external process)

Table ``domain_flag`` should represent history of flags being enabled and disabled on domains during time. For simplicity we can assume that individual flags are independent on each other and records for given domain can overlap in time. Each flag can be valid for some period of time. It always starts at specific time but the upper limit can be unbounded which means that it is valid indefinitely. We never change already inserted records with one exception: if upper limit is unbounded, it can be set to specific point in time but never to the past (at the time the change is made).
*/
CREATE TABLE domain_flag (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER NOT NULL REFERENCES domain(id) ON DELETE CASCADE,
    flag VARCHAR(32) NOT NULL,
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMP WITH TIME ZONE,

    CONSTRAINT domain_flag_flag_not_empty CHECK (LENGTH(TRIM(flag)) > 0),
    CONSTRAINT domain_flag_validity_order CHECK (
        valid_to IS NULL OR valid_to > valid_from
    )
    --for valid flag values
    CONSTRAINT domain_flag_valid_types CHECK (
        flag IN ('EXPIRED', 'OUTZONE', 'DELETE_CANDIDATE')
    ),
    -- Prevent setting valid_to to the past
    CONSTRAINT domain_flag_no_past_closure CHECK (
        valid_to IS NULL OR valid_to >= NOW()
    )
);