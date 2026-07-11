import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from renderer import build_html

BASE_DIR = Path(__file__).parent
OUTPUT = BASE_DIR / "output.html"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spell Card Printer")
        self.geometry("740x640")

        self.all_spells = []
        self._load_files()

        self.check_vars = {}
        self.filtered = list(self.all_spells)

        self._build_ui()
        self._refresh_list()
        self.border_image_path = ""

    def _load_files(self):
        for year, fname in [("2014", "spells2014.json"), ("2024", "spells2024.json")]:
            p = BASE_DIR / fname
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    for spell in json.load(f):
                        self.all_spells.append((spell, year))

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        pad = {"padx": 8}

        # filter row
        row1 = tk.Frame(self, pady=5)
        row1.pack(fill=tk.X, **pad)
        tk.Label(row1, text="Source:").pack(side=tk.LEFT)
        self.source = tk.StringVar(value="All")
        for source_option in ("All", "2014", "2024"):
            tk.Radiobutton(row1, text=source_option, variable=self.source, value=source_option,
                           command=self._apply_filter).pack(side=tk.LEFT)

        tk.Label(row1, text="   Level:").pack(side=tk.LEFT)
        self.lvl = tk.StringVar(value="All")
        lvl_cb = ttk.Combobox(row1, textvariable=self.lvl, state="readonly", width=8,
                               values=["All", "Cantrip"] + [str(i) for i in range(1, 10)])
        lvl_cb.pack(side=tk.LEFT, padx=2)
        lvl_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        tk.Label(row1, text="   School:").pack(side=tk.LEFT)
        self.school = tk.StringVar(value="All")
        schools = ["All"] + sorted({
            s.get("school", "").capitalize()
            for s, _ in self.all_spells if s.get("school")
        })
        sch_cb = ttk.Combobox(row1, textvariable=self.school, state="readonly", width=13,
                              values=schools)
        sch_cb.pack(side=tk.LEFT, padx=2)
        sch_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        tk.Label(row1, text="   Class:").pack(side=tk.LEFT)
        self.dnd_class = tk.StringVar(value="All")
        classes = ["All"] + sorted({
            c.capitalize()
            for s, _ in self.all_spells
            for c in s.get("classes", [])
        })
        cls_cb = ttk.Combobox(row1, textvariable=self.dnd_class, state="readonly", width=10,
                              values=classes)
        cls_cb.pack(side=tk.LEFT, padx=2)
        cls_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        # search row
        row2 = tk.Frame(self, pady=2)
        row2.pack(fill=tk.X, **pad)
        tk.Label(row2, text="Search:").pack(side=tk.LEFT)
        self.custom_search = tk.StringVar()
        self.custom_search.trace_add("write", lambda *_: self._apply_filter())
        tk.Entry(row2, textvariable=self.custom_search, width=30).pack(side=tk.LEFT, padx=4)
        tk.Button(row2, text="Border Select", command=self.select_border).pack(side=tk.RIGHT)

        # action row
        row3 = tk.Frame(self, pady=2)
        row3.pack(fill=tk.X, **pad)
        tk.Button(row3, text="Select All",  command=self._select_all).pack(side=tk.LEFT)
        tk.Button(row3, text="Select None", command=self._select_none).pack(side=tk.LEFT, padx=4)
        self.status_lbl = tk.Label(row3, text="0 selected")
        self.status_lbl.pack(side=tk.RIGHT)

        # scrollable checklist
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, **pad)

        sb = ttk.Scrollbar(frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.cv = tk.Canvas(frame, yscrollcommand=sb.set, bg="white", highlightthickness=0)
        self.cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self.cv.yview)

        self.inner = tk.Frame(self.cv, bg="white")
        self.win_id = self.cv.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.cv.config(scrollregion=self.cv.bbox("all")))
        self.cv.bind("<Configure>",
                     lambda e: self.cv.itemconfig(self.win_id, width=e.width))
        for w in (self.cv, self.inner):
            w.bind("<MouseWheel>",
                   lambda e: self.cv.yview_scroll(-1 * (e.delta // 120), "units"))

        # generate button
        tk.Button(self, text="Generate & Open HTML",
                  command=self._generate,
                  bg="#2a7a45", fg="white",
                  font=("", 11, "bold"), pady=6
                  ).pack(fill=tk.X, padx=8, pady=8)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _key(self, spell, source):
        return (spell["name"], source)

    def _lvl_key(self, spell, source):
        lv = spell.get("level", "")
        if source == "2014":
            return "cantrip" if lv == "cantrip" else str(lv)
        return "cantrip" if lv == 0 else str(lv)

    # ── filter + list ─────────────────────────────────────────────────────────

    def _apply_filter(self):
        source = self.source.get()
        lvl = self.lvl.get().lower()
        school = self.school.get().lower()
        dnd_class = self.dnd_class.get().lower()
        q   = self.custom_search.get().lower()
        self.filtered = [
            (s, r) for s, r in self.all_spells
            if (source == "All" or r == source)
            and (lvl == "all" or self._lvl_key(s, r) == lvl)
            and (school == "all" or s.get("school", "").lower() == school)
            and (dnd_class == "all" or dnd_class in [c.lower() for c in s.get("classes", [])])
            and (not q or q in s.get("name", "").lower())
        ]
        self._refresh_list()

    def _refresh_list(self):
        for w in self.inner.winfo_children():
            w.destroy()
        for spell, source in self.filtered:
            key = self._key(spell, source)
            if key not in self.check_vars:
                self.check_vars[key] = tk.BooleanVar(value=False)
            lk     = self._lvl_key(spell, source).capitalize()
            school = spell.get("school", "").capitalize()
            label  = f"[{source}]  {spell['name']}   {lk} · {school}"
            tk.Checkbutton(
                self.inner, text=label, variable=self.check_vars[key],
                anchor="w", bg="white", command=self._update_status
            ).pack(fill=tk.X, padx=4, pady=1)
        self._update_status()

    def _update_status(self):
        n = sum(1 for v in self.check_vars.values() if v.get())
        if n == 0:
            self.status_lbl.config(text="0 selected")
        else:
            pages = -(-n // 9)
            self.status_lbl.config(text=f"{n} selected · {pages} page{'s' if pages != 1 else ''}")

    def _select_all(self):
        for s, r in self.filtered:
            self.check_vars[self._key(s, r)].set(True)
        self._update_status()

    def _select_none(self):
        for s, r in self.filtered:
            self.check_vars[self._key(s, r)].set(False)
        self._update_status()

    # ── generate ──────────────────────────────────────────────────────────────

    def _generate(self):
        selected = []
        for source, year in self.all_spells:
            check_value = self.check_vars.get(self._key(source, year))
            if check_value and check_value.get():
                selected.append((source, year))

        if not selected:
            messagebox.showwarning("Nothing selected", "Select at least one spell first.")
            return

        with open(OUTPUT, "w", encoding="utf-8") as f:
            f.write(build_html(selected, self.border_image_path))
        import webbrowser
        webbrowser.open(OUTPUT.as_uri())

    def select_border(self):
        path = filedialog.askopenfilename(
            title="Select Card Border Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        )
        if path:
            self.border_image_path = path