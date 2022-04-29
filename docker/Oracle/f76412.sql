DROP TABLE F76412;
COMMIT;

CREATE TABLE F76412 
(
  IJITM NUMBER NOT NULL 
, IJMCU CHAR(12 BYTE) NOT NULL 
, IJLOCN CHAR(20 BYTE) NOT NULL 
, IJLOTN CHAR(30 BYTE) NOT NULL 
, IJBCLF CHAR(10 BYTE) 
, IJBCTF CHAR(2 BYTE) 
, IJBICN CHAR(1 BYTE) 
, IJBIST CHAR(1 BYTE) 
, IJBORI CHAR(1 BYTE) 
, IJBCFC CHAR(3 BYTE) 
, IJBINM CHAR(10 BYTE) 
, IJUSER CHAR(10 BYTE) 
, IJPID CHAR(10 BYTE) 
, IJJOBN CHAR(10 BYTE) 
, IJUPMJ NUMBER(6, 0) 
, IJTDAY NUMBER 
, IJBRRTIR NUMBER 
, IJBRRD NUMBER 
, IJBRKINS CHAR(1 BYTE) 
, CONSTRAINT F76412_PK PRIMARY KEY 
  (
    IJITM 
  , IJMCU 
  , IJLOCN 
  , IJLOTN 
  )
  ENABLE 
);

CREATE UNIQUE INDEX F76412_0 ON F76412 (IJITM ASC, IJMCU ASC, IJLOCN ASC, IJLOTN ASC);

comment on column f76412.IJITM is 'Item Number - Short';
comment on column f76412.IJMCU is 'Business Unit';
comment on column f76412.IJLOCN is 'Location';
comment on column f76412.IJLOTN is 'Lot/Serial Number';
comment on column f76412.IJBCLF is 'Fiscal Classification';
comment on column f76412.IJBCTF is 'ICMS/IPI Tax Summary';
comment on column f76412.IJBICN is 'Government Controlled Item';
comment on column f76412.IJBIST is 'ICMS Tax Substitution Mark-up';
comment on column f76412.IJBORI is 'Item Origin';
comment on column f76412.IJBCFC is 'Purchase Use';
comment on column f76412.IJBINM is 'Print Message - Fiscal Purpose';
comment on column f76412.IJUSER is 'User ID';
comment on column f76412.IJPID is 'Program ID';
comment on column f76412.IJJOBN is 'Work Station ID';
comment on column f76412.IJUPMJ is 'Date - Updated';
comment on column f76412.IJTDAY is 'Time of Day';
comment on column f76412.IJBRRTIR is 'Retention of IR';
comment on column f76412.IJBRRD is 'Reduction of IR';
comment on column f76412.IJBRKINS is 'INSS (S/N)';

REM INSERTING into F76412
SET DEFINE OFF;
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     ERCTTV2','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','MATEUS_F  ','SQL       ','RBST9134  ','114013','184600','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NERI008','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NERI009','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NPCCR05','                    ','                              ','99999999  ','00','0','N','0','PNC','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NPCCR07','                    ','                              ','99999999  ','00','0','N','0','PNC','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NPCCR90','                    ','                              ','99999999  ','00','0','N','0','PNC','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NPIMR01','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NRCAC01','                    ','                              ','99999999  ','00','0','N','0','PID','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NRCAC02','                    ','                              ','99999999  ','00','0','N','0','PNC','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NRIBA06','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NRICS06','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NRICS13','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NRICS14','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NRIPL01','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NRIPL06','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NRIRG04','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NSCFL01','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('0','     NSCFL22','                    ','                              ','99999999  ','00','0','N','0','PNA','          ','FERNANDO  ','R5541001  ','FOCUS 606 ','0','103047','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('9','     ERCRAP1','                    ','                              ','85408910  ','10','0','N','1','PIA','          ','L_DUTRA   ','P76412B   ','MEPOAE145 ','102161','193427','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('44','     ERCTTG2','                    ','                              ','48204000  ','02','0','N','0','PNA','          ','L_DUTRA   ','P76412B   ','MEPOAE145 ','102144','161513','0','0',' ');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('89','     ERCTTG1','                    ','                              ','40059190  ','01','0','N','0','PNA','          ','CLEBER_F  ','P76412B   ','CORPOAE412','103324','91854','0','0','0');
Insert into F76412 (IJITM,IJMCU,IJLOCN,IJLOTN,IJBCLF,IJBCTF,IJBICN,IJBIST,IJBORI,IJBCFC,IJBINM,IJUSER,IJPID,IJJOBN,IJUPMJ,IJTDAY,IJBRRTIR,IJBRRD,IJBRKINS) values ('89','     ERCTTG1','054021000000        ','                              ','40059190  ','01','0','N','0','PNA','          ','CLEBER_F  ','P76412B   ','CORPOAE412','103324','91901','0','0','0');
commit;

exit;