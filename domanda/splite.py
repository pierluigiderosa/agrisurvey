from shutil import copy2


from pysqlite2 import dbapi2 as sqlite3


# prendo un danno per prova
def make(danno, pk,sqlitedb):
    dn = danno.objects.get(id=pk)
    copy2('master.sqlite', sqlitedb)
    # creating/connecting the test_db
    conn = sqlite3.connect(sqlitedb)
    conn.enable_load_extension(True)
    # initializing Spatial MetaData
    # using v.2.4.0 this will automatically create
    # GEOMETRY_COLUMNS and SPATIAL_REF_SYS
    conn.execute("SELECT load_extension('mod_spatialite');")

    # creating a POLYGON table
    sql = 'CREATE TABLE danni ('
    sql += 'id INTEGER NOT NULL PRIMARY KEY,'
    sql += 'codice_danno INTEGER NOT NULL,'
    sql += 'richiedente TEXT NOT NULL,'
    sql += 'coltura TEXT NOT NULL,'
    sql += 'varieta TEXT,'
    sql += 'SumTot REAL NOT NULL,'
    sql += 'SumSem REAL NOT NULL,'
    sql += 'PercDanno INTEGER NOT NULL,'
    sql += 'Produzione INTEGER NOT NULL,'
    sql += 'PerProdPersa INTEGER NOT NULL,'
    sql += 'ValoreDanno INTEGER NOT NULL,'
    sql += 'NumPianteDan INTEGER,'
    sql += 'TipoPiante TEXT,'
    sql += 'SelvagginaSem TEXT NOT NULL,'
    sql += 'OpereProtezione TEXT,'
    sql += 'stato_pratica TEXT NOT NULL,'
    sql += 'foglio TEXT NOT NULL,'
    sql += 'particella TEXT NOT NULL)'
    conn.execute(sql)
    # creating a POLYGON Geometry column
    sql = "SELECT AddGeometryColumn('danni', "
    sql += "'geom', 3003, 'MULTIPOLYGON', 'XY')"
    conn.execute(sql)

    # inserting POLYGONs
    catastali = dn.fog_part_certified.all()
    for i in range(len(catastali)):
        catastale_i = catastali[i]
        catastale_i.mpoly.transform(3003)
        geometria = "GeomFromText('"
        geometria += catastale_i.mpoly.wkt
        geometria += "', 3003)"
        sql = "INSERT INTO danni (id, codice_danno, richiedente,coltura,varieta,SumTot,SumSem,PercDanno,Produzione,PerProdPersa ,ValoreDanno,NumPianteDan,TipoPiante,SelvagginaSem, OpereProtezione,stato_pratica,foglio,particella, geom) "
        sql += "VALUES (%d, %d, '%s', '%s', '%s', %d, %d, %d, %d, %d, %d, %d , '%s', '%s', '%s', '%s', '%s', '%s', %s)" % (i+1,
        dn.id, str(dn.richiedente), dn.coltura, dn.varieta, dn.SumTot, dn.SumSem, dn.PercDanno, dn.Produzione,
        dn.PerProdPersa, dn.ValoreDanno, dn.NumPianteDan, dn.TipoPiante, dn.SelvagginaSem, dn.OpereProtezione,
        dn.stato_pratica, catastale_i.foglio, catastale_i.part, geometria)
        conn.execute(sql)

    conn.commit()
    conn.execute("SELECT CreateSpatialIndex('danni', 'geom');")

    # update layer statistic required by geopaparazzi
    sql = "SELECT UpdateLayerStatistics()"
    conn.execute(sql)

    # checking POLYGONs
    sql = "SELECT DISTINCT Count(*), ST_GeometryType(geom), "
    sql += "ST_Srid(geom) FROM danni"
    rs = conn.execute(sql)
    for row in rs:
        msg = "> Inserted %d entities of type " % (row[0])
        msg += "%s SRID=%d" % (row[1], row[2])
        print msg

    rs.close()

    conn.enable_load_extension(False)
    conn.close()


#makeSpatialite(danno,2,'pippo')