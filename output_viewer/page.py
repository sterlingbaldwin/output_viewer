from .htmlbuilder import Document, Table, TableCell, Link
import os
from .examine import is_img, is_data
from .utils import slugify, nuke_and_pave


class Column(object):
    def __init__(self, row, spec):
        self.row = row
        self.path = spec.get("path", None)
        self.title = spec.get("title", None)
        if self.title is None:
            self.title = os.path.basename(os.path.splitext(self.path)[0])
        self.meta = spec.get("meta", {})

    def build(self, toolbar):
        doc = Document(title=self.title, level=3)
        doc.append(toolbar)
        container = doc.append_tag("div", class_="container")
        row = container.append_tag("div", class_="row")
        title = row.append_tag("h1")
        title.append(self.title)

        row = container.append_tag('div', class_="row")
        col = row.append_tag("div", class_="col-sm-12")
        # Root/Plotset/Group/Row/this.html
        file_url = os.path.join("..", "..", "..", self.path)
        file_div = col.append_tag("div", class_="img_display")
        if is_img(self.path):
            file_div.append_tag('div').append_tag("img", src=file_url)
        link = file_div.append_tag('div').append_tag("a", href=file_url, download="")
        link.append("Download File")

        table = Table()
        header = table.append_header()
        header.append_cell("Metadata Key")
        header.append_cell("Metadata Value")
        for k, v in self.meta.iteritems():
            r = table.append_row()
            r.append_cell(k)
            r.append_cell(v)

        container.append_tag("div", class_="row").append(table)

        with open(self.getURL(), "w") as out:
            toolbar.setLevel(3)
            out.write(doc.build())

    def getURL(self):
        return os.path.join(self.row.dirname, slugify(self.title) + ".html")

    def getLink(self, level):
        l = Link(href=self.getURL(), data={"preview": os.path.join(*([".."] * level + [self.path]))})
        l.append(self.title)
        return l


class Row(object):
    def __init__(self, group, spec):
        self.group = group
        self.title = slugify(spec["title"])
        self.cols = {}
        for i, c in enumerate(spec["columns"]):
            if isinstance(c, dict):
                self.cols[i] = Column(self, c)
            else:
                # We don't actually need to keep track of the "string" columns
                # They'll just be plain text
                continue
        self.dirname = os.path.join(self.group.dirpath, self.title)

    def getLink(self, col_ind, level):
        if col_ind in self.cols:
            return self.cols[col_ind].getLink(level)
        else:
            return None

    def build(self, toolbar):
        nuke_and_pave(self.dirname)
        for _, col in self.cols.iteritems():
            col.build(toolbar)


class Group(object):
    def __init__(self, root, parent, spec, rows):
        title = spec["title"]
        self.dirname = slugify(title)
        self.parent = parent
        self.dirpath = os.path.join(root, parent, self.dirname)
        self.rows = []
        for row in rows:
            self.rows.append(Row(self, row))

    def getLink(self, row_ind, col_ind, level):
        return self.rows[row_ind].getLink(col_ind, level)

    def build(self, toolbar):
        nuke_and_pave(self.dirpath)
        for r in self.rows:
            r.build(toolbar)


class Page(object):
    def __init__(self, spec, root_path="./"):
        self.name = spec.get("title", "")
        if "menu" in spec:
            self.menu = {}
            if isinstance(spec["menu"], dict):
                self.menu = spec["menu"]
            else:
                self.menu["title"] = spec["menu"]
        else:
            self.menu = None
        self.short_name = spec.get("short_name", None)

        columns = spec.get("columns", [])

        self.number_of_cols = len(columns)

        groups = spec.get("groups", [])
        self.groups = []
        for g in groups:
            if isinstance(g, (str, unicode)):
                self.groups.append({"title": g, "columns": columns})
            elif isinstance(g, dict):
                if "columns" not in g:
                    g["columns"] = columns
                self.number_of_cols = max(len(g["columns"]), self.number_of_cols)
                self.groups.append(g)
        self.root_path = root_path
        self.description = spec.get("description", "")
        self.icon = spec.get("icon", None)
        self.rows = spec.get("rows", [])
        self.long_desc = spec.get("long_description", "")

    def build(self, dirname, toolbar):
        nuke_and_pave(os.path.join(self.root_path, dirname))

        doc = Document(title=self.name, level=1)
        # Calling classes should provide a toolbar
        doc.append(toolbar)
        # Build the header, title, subtitle, etc.
        container = doc.append_tag("div", class_="container")
        row = container.append_tag("div", class_="row")
        title = row.append_tag("h1")
        if self.icon is not None and os.path.exists(os.path.join(self.root_path, self.icon)):
            title.append_tag("img", src="../" + self.icon, width="200px", alt=self.name)
        title.append(self.name)
        if self.description:
            subtitle = row.append_tag("h2")
            subtitle.append(self.description)
        if self.long_desc:
            b = row.append_tag('b')
            b.append_formatted(self.long_desc)
        row.append_tag("hr")

        # Start the actual body of the output set
        row = container.append_tag("div", class_="row")
        col = row.append_tag("div", class_="col-sm-12")
        table = Table(class_="table")
        col.append(table)

        for group_ind, rows in enumerate(self.rows):
            group = self.groups[group_ind]
            column_names = group["columns"]
            group_title = group["title"]

            # Pad the columns so they're appropriately spaced
            column_widths = [1 for i in range(len(column_names))]
            difflen = self.number_of_cols - len(column_names)
            col_ind = len(column_widths) - 1
            while difflen > 0:
                column_widths[col_ind] += 1
                difflen -= 1
                col_ind = (col_ind - 1) % len(column_widths)

            header = table.append_header()
            column_widths = [str(i) for i in column_widths]
            # Title
            header.append_cell(group_title)
            for col_ind in range(len(column_names)):
                header.append_cell(column_names[col_ind], colspan=column_widths[col_ind])

            group_obj = Group(self.root_path, dirname, group, rows)

            for row_ind, r in enumerate(rows):
                tr = table.append_row()
                cell = TableCell()
                cell.append_formatted("<span>%s</span>" % r["title"])
                tr.append(cell)
                for col_ind, col in enumerate(r["columns"]):
                    l = group_obj.getLink(row_ind, col_ind, 1)
                    if l is None:
                        l = col
                    tr.append_cell(l)

            group_obj.build(toolbar)

        with open(os.path.join(self.root_path, dirname, "index.html"), "w") as outfile:
            toolbar.setLevel(1)
            outfile.write(doc.build())
