import logging

from visidata import VisiData, Sheet, Progress, ColumnItem, anytype, vd

SASTypes = {
    'string': str,
    'number': float,
}

@VisiData.api
def open_xpt(vd, p):
    return XptSheet(p.base_stem, source=p)

@VisiData.api
def open_sas7bdat(vd, p):
    return SasSheet(p.base_stem, source=p)

class XptSheet(Sheet):
    def iterload(self):
        xport = vd.importExternal('xport')
        with open(self.source, 'rb') as fp:
            self.rdr = xport.Reader(fp)

            self.columns = []
            for i, var in enumerate(self.rdr._variables):
                self.addColumn(ColumnItem(var.name, i, type=float if var.numeric else str))

            # a visidata row must not be a tuple, so convert each tuple to a list
            for t in self.rdr:
                yield list(t)


class SasSheet(Sheet):
    def iterload(self):
        sas7bdat = vd.importExternal('sas7bdat')
        self.dat = sas7bdat.SAS7BDAT(str(self.source), skip_header=True, log_level=logging.CRITICAL)
        self.columns = []
        for col in self.dat.columns:
            self.addColumn(ColumnItem(col.name.decode('utf-8'), col.col_id, type=SASTypes.get(col.type, anytype)))

        with self.dat as fp:
            yield from Progress(fp, total=self.dat.properties.row_count)
