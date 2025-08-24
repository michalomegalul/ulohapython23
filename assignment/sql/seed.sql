--Get domains that are registered and NOT expired
SELECT d.fqdn
FROM domain d
WHERE d.unregistered_at IS NULL
  AND d.id NOT IN (
    SELECT df.domain_id 
    FROM domain_flag df 
    WHERE df.flag = 'EXPIRED' 
        AND df.valid_to IS NULL
  )
ORDER BY d.fqdn;

--GEt domains that had expired and OUTZONE flags
SELECT DISTINCT d.fqdn
FROM domain d
JOIN domain_flag df1 ON d.id = df1.domain_id
JOIN domain_flag df2 ON d.id = df2.domain_id
WHERE df1.flag = 'EXPIRED'
  AND df2.flag = 'OUTZONE'
ORDER BY d.fqdn;