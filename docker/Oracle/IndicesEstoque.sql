CREATE OR REPLACE VIEW f4111_tot AS
SELECT
    *
FROM
    (
        SELECT
            mcco     ttco,
            illitm   ttlitm,
            ilmcu    ttmcu,
            illocn   ttlocn,
            ildgl    ttdgl,
            ildct    ttdct,
            imuom1   ttuom1,
            iltrum   tttrum,
            ilglpt   ttglpt,
            SUM(iltrqt) tttrqt,
            SUM(ilpaid) ttpaid
        FROM
            (
                SELECT
                    f0006.mcco,
                    f4111.illitm,
                    f4111.ilmcu,
                    f4111.illocn,
                    to_char(to_date(f4111.ildgl + 1900000, 'YYYYDDD'), 'YYYYMM') ildgl,
                    f4101.imuom1,
                    f4111.iltrum,
                    f4111.ildct,
                    f4111.iltrqt,
                    f4111.ilglpt,
                    f4111.iluncs,
                    f4111.ilpaid
                FROM
                    f4111   f4111
                    INNER JOIN f0006   f0006 ON f4111.ilmcu = f0006.mcmcu
                    INNER JOIN f4101   f4101 ON f4111.ilitm = f4101.imitm
                WHERE
                    1 = 1
            )
        GROUP BY
            mcco,
            illitm,
            ilmcu,
            illocn,
            ildgl,
            ildct,
            imuom1,
            iltrum,
            ilglpt
    )
WHERE
    tttrqt <> 0
    OR ttpaid <> 0
ORDER BY
    ttco,
    ttlitm,
    ttmcu,
    ttdgl,
    ttlocn,
    ttuom1,
    ttglpt,
    ttdct;

CREATE OR REPLACE VIEW f41112_tot AS
    SELECT
        mcco     ttco,
        inlitm   ttlitm,
        inmcu    ttmcu,
        inlocn   ttlocn,
        ildgl    ttdgl,
        imuom1   ttuom1,
        ilglpt   ttglpt,
        SUM(iltrqt) tttrqt,
        SUM(ilpaid) ttpaid
    FROM
        (
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '00' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.incmqt   iltrqt,
                f41112.incuma   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '01' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq01   iltrqt,
                f41112.inan01   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '02' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq02   iltrqt,
                f41112.inan02   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '03' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq03   iltrqt,
                f41112.inan03   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '04' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq04   iltrqt,
                f41112.inan04   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '05' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq05   iltrqt,
                f41112.inan05   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '06' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq06   iltrqt,
                f41112.inan06   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '07' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq07   iltrqt,
                f41112.inan07   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '08' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq08   iltrqt,
                f41112.inan08   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '09' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq09   iltrqt,
                f41112.inan09   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '10' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq10   iltrqt,
                f41112.inan10   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '11' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq11   iltrqt,
                f41112.inan11   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
            UNION ALL
            SELECT
                f0006.mcco,
                f41112.inlitm,
                f41112.inmcu,
                f41112.inlocn,
                f41112.inctry
                || lpad(f41112.infy, 2, '0')
                || '12' ildgl,
                f4101.imuom1,
                f41112.inglpt   ilglpt,
                f41112.innq12   iltrqt,
                f41112.inan12   ilpaid
            FROM
                f41112   f41112
                INNER JOIN f0006    f0006 ON f41112.inmcu = f0006.mcmcu
                INNER JOIN f4101    f4101 ON f41112.initm = f4101.imitm
        )
    WHERE
        iltrqt <> 0
        OR ilpaid <> 0
    GROUP BY
        mcco,
        inlitm,
        inmcu,
        inlocn,
        ildgl,
        imuom1,
        ilglpt
    ORDER BY
        mcco,
        inlitm,
        inmcu,
        inlocn,
        ildgl,
        imuom1,
        ilglpt;

CREATE OR REPLACE VIEW f4111_det AS
    SELECT
        *
    FROM
        (
            SELECT
                mcco     ttco,
                illitm   ttlitm,
                ilmcu    ttmcu,
                illocn   ttlocn,
                ildgl    ttdgl,
                ildct    ttdct,
                imuom1   ttuom1,
                iltrum   tttrum,
                ilglpt   ttglpt,
                SUM(iltrqt) tttrqt,
                SUM(ilpaid) ttpaid
            FROM
                (
                    SELECT
                        f0006.mcco,
                        f4111.illitm,
                        f4111.ilmcu,
                        f4111.illocn,
                        to_date(f4111.ildgl + 1900000, 'YYYYDDD') ildgl,
                        f4101.imuom1,
                        f4111.iltrum,
                        f4111.ildct,
                        f4111.iltrqt,
                        f4111.ilglpt,
                        f4111.iluncs,
                        f4111.ilpaid
                    FROM
                        f4111   f4111
                        INNER JOIN f0006   f0006 ON f4111.ilmcu = f0006.mcmcu
                        INNER JOIN f4101   f4101 ON f4111.ilitm = f4101.imitm
                    WHERE
                        1 = 1
                )
            GROUP BY
                mcco,
                illitm,
                ilmcu,
                illocn,
                ildgl,
                ildct,
                imuom1,
                iltrum,
                ilglpt
        )
    WHERE
        tttrqt <> 0
        OR ttpaid <> 0
    ORDER BY
        ttco,
        ttlitm,
        ttmcu,
        ttlocn,
        ttdgl,
        ttuom1,
        ttglpt,
        ttdct;

SELECT
    *
FROM
    f4111_det;

SELECT
    *
FROM
    f4111_tot;

SELECT
    *
FROM
    f41112_tot
WHERE
    substr(ttdgl, 5, 2) <> '00';
    
SELECT
    nvl(jde_converte_um('     ERCTMI2',1, 'PC', 'UN'),1) CONV
FROM
    dual;

exit;