CREATE OR REPLACE FUNCTION jde_converte_um (
    szfilial   CHAR,
    nitm       NUMBER,
    szde       CHAR,
    szpara     CHAR
) RETURN NUMBER AS
    conv NUMBER;
BEGIN
    IF szde <> szpara THEN
        SELECT
            nvl(conv, 1)
        INTO conv
        FROM
            (
                SELECT
                    ( (case when umconv = 0 then 1 else umconv end) / 10000000 ) conv
                FROM
                    f41002
                WHERE
                    umitm = nitm
                    AND umum = szde
                    AND umrum = szpara
                UNION ALL
                SELECT
                    ( (case when ucconv = 0 then 1 else ucconv end) / 10000000 ) conv
                FROM
                    f41003
                WHERE
                    ucum = szde
                    AND ucrum = szpara
                UNION ALL
                SELECT
                    1 / ( (case when umconv = 0 then 1 else umconv end) / 10000000 ) conv
                FROM
                    f41002
                WHERE
                    umitm = nitm
                    AND umum = szpara
                    AND umrum = szde
                UNION ALL
                SELECT
                    1 / ( (case when ucconv = 0 then 1 else ucconv end) / 10000000 ) conv
                FROM
                    f41003
                WHERE
                    ucum = szpara
                    AND ucrum = szde
            )
        WHERE
            ROWNUM = 1;

        RETURN conv;
    ELSE
        RETURN 1;
    END IF;
END jde_converte_um;

exit;