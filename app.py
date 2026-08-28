"""
He thong Quan ly Do an Mon hoc — chuc nang Dang ky de tai (UC07)
Chay:  python app.py
Mo:    http://127.0.0.1:5000
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "do_an.db"
HOC_KY = "Hoc ky 1, 2025-2026"

app = Flask(__name__)
app.secret_key = "dev-ql-do-an-mon-hoc-uc07"


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS nguoi_dung (
            ma_nd INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_dang_nhap TEXT UNIQUE NOT NULL,
            mat_khau TEXT NOT NULL,
            ho_ten TEXT NOT NULL,
            vai_tro TEXT NOT NULL CHECK (vai_tro IN ('SV','GV','GVK')),
            ma_so TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS de_tai (
            ma_dt INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_de_tai TEXT NOT NULL,
            mo_ta TEXT NOT NULL,
            yeu_cau_ky_thuat TEXT NOT NULL,
            chuyen_nganh TEXT NOT NULL,
            so_luong_toi_da INTEGER NOT NULL CHECK (so_luong_toi_da >= 1),
            so_luong_da_dk INTEGER NOT NULL DEFAULT 0 CHECK (so_luong_da_dk >= 0),
            ma_gv INTEGER NOT NULL REFERENCES nguoi_dung(ma_nd),
            trang_thai TEXT NOT NULL DEFAULT 'MO' CHECK (trang_thai IN ('MO','DAY','DONG')),
            hoc_ky TEXT NOT NULL,
            CHECK (so_luong_da_dk <= so_luong_toi_da)
        );

        CREATE TABLE IF NOT EXISTS dang_ky (
            ma_dk INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_dt INTEGER NOT NULL REFERENCES de_tai(ma_dt),
            ma_sv INTEGER NOT NULL REFERENCES nguoi_dung(ma_nd),
            ngay_dang_ky TEXT NOT NULL,
            trang_thai TEXT NOT NULL DEFAULT 'HIEU_LUC' CHECK (trang_thai IN ('HIEU_LUC','HUY')),
            UNIQUE (ma_sv, trang_thai)
        );
        """
    )
    if db.execute("SELECT COUNT(*) FROM nguoi_dung").fetchone()[0] == 0:
        users = [
            ("2112345", "123456", "Nguyen Van An", "SV", "2112345"),
            ("2112346", "123456", "Tran Thi Binh", "SV", "2112346"),
            ("2112347", "123456", "Le Minh Cuong", "SV", "2112347"),
            ("2112001", "123456", "Pham Quoc Dung", "SV", "2112001"),
            ("2112002", "123456", "Vo Ngoc Em", "SV", "2112002"),
            ("2112003", "123456", "Dang Hai Phong", "SV", "2112003"),
            ("gv001", "123456", "TS. Tran Minh Duc", "GV", "GV001"),
            ("gv002", "123456", "ThS. Le Thi Hoa", "GV", "GV002"),
            ("gv003", "123456", "TS. Pham Quoc Huy", "GV", "GV003"),
            ("gvk01", "123456", "Nguyen Thi Giao Vu", "GVK", "GVK01"),
        ]
        db.executemany(
            "INSERT INTO nguoi_dung(ten_dang_nhap, mat_khau, ho_ten, vai_tro, ma_so) VALUES (?,?,?,?,?)",
            users,
        )
        gv = {r["ma_so"]: r["ma_nd"] for r in db.execute("SELECT ma_nd, ma_so FROM nguoi_dung")}
        topics = [
            (
                "He thong quan ly do an mon hoc tren nen tang web",
                "Xay dung web app dang ky de tai, nop tien do tuan, cham diem va xuat thong ke cho giao vu.",
                "Java Spring / React, JWT, PostgreSQL",
                "Web / Backend",
                4,
                0,
                gv["GV001"],
                "MO",
                HOC_KY,
            ),
            (
                "Chatbot ho tro tu van dang ky hoc phan bang tieng Viet",
                "Xay dung chatbot tra loi cau hoi ve chuong trinh dao tao, dung du lieu noi bo khoa.",
                "Python, LLM API, RAG, FastAPI",
                "AI / NLP",
                3,
                0,
                gv["GV002"],
                "MO",
                HOC_KY,
            ),
            (
                "Ung dung theo doi tien do do an tren Android",
                "App cho sinh vien nop tien do va nhan nhan xet tu giang vien theo tuan.",
                "Kotlin, Firebase, thong bao push",
                "Mobile",
                3,
                3,
                gv["GV003"],
                "DAY",
                HOC_KY,
            ),
        ]
        db.executemany(
            """INSERT INTO de_tai(ten_de_tai, mo_ta, yeu_cau_ky_thuat, chuyen_nganh,
               so_luong_toi_da, so_luong_da_dk, ma_gv, trang_thai, hoc_ky)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            topics,
        )
        android = db.execute(
            "SELECT ma_dt FROM de_tai WHERE chuyen_nganh = 'Mobile'"
        ).fetchone()["ma_dt"]
        now = "2026-08-20 09:00:00"
        for ma_so in ("2112001", "2112002", "2112003"):
            ma_sv = db.execute(
                "SELECT ma_nd FROM nguoi_dung WHERE ma_so = ?", (ma_so,)
            ).fetchone()["ma_nd"]
            db.execute(
                "INSERT INTO dang_ky(ma_dt, ma_sv, ngay_dang_ky, trang_thai) VALUES (?,?,?, 'HIEU_LUC')",
                (android, ma_sv, now),
            )
    db.commit()
    db.close()


def login_required(role: str | None = None):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "ma_nd" not in session:
                flash("Vui long dang nhap.", "error")
                return redirect(url_for("login"))
            if role and session.get("vai_tro") != role:
                flash("Ban khong co quyen dung chuc nang nay.", "error")
                return redirect(url_for("home"))
            return fn(*args, **kwargs)

        return wrapper

    return deco


def current_user():
    if "ma_nd" not in session:
        return None
    return get_db().execute(
        "SELECT * FROM nguoi_dung WHERE ma_nd = ?", (session["ma_nd"],)
    ).fetchone()


def dang_ky_hieu_luc(ma_sv: int):
    return get_db().execute(
        """
        SELECT dk.*, dt.ten_de_tai, dt.ma_dt
        FROM dang_ky dk
        JOIN de_tai dt ON dt.ma_dt = dk.ma_dt
        WHERE dk.ma_sv = ? AND dk.trang_thai = 'HIEU_LUC'
        """,
        (ma_sv,),
    ).fetchone()


@app.route("/")
def home():
    if "ma_nd" not in session:
        return redirect(url_for("login"))
    if session.get("vai_tro") == "SV":
        return redirect(url_for("danh_sach_de_tai"))
    return redirect(url_for("de_tai_cua_toi"))


@app.route("/dang-nhap", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ten = (request.form.get("ten_dang_nhap") or "").strip()
        mk = request.form.get("mat_khau") or ""
        user = get_db().execute(
            "SELECT * FROM nguoi_dung WHERE ten_dang_nhap = ? AND mat_khau = ?",
            (ten, mk),
        ).fetchone()
        if not user:
            flash("Thong tin dang nhap khong dung.", "error")
            return render_template("login.html")
        session.clear()
        session["ma_nd"] = user["ma_nd"]
        session["vai_tro"] = user["vai_tro"]
        session["ho_ten"] = user["ho_ten"]
        session["ma_so"] = user["ma_so"]
        flash("Xin chao " + user["ho_ten"] + ".", "ok")
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/dang-xuat")
def logout():
    session.clear()
    flash("Da dang xuat.", "ok")
    return redirect(url_for("login"))


@app.route("/de-tai")
@login_required("SV")
def danh_sach_de_tai():
    q = (request.args.get("q") or "").strip().lower()
    gv_filter = request.args.get("gv") or ""
    slot_filter = request.args.get("slot") or "con_cho"

    db = get_db()
    topics = db.execute(
        """
        SELECT dt.*, gv.ho_ten AS ten_gv
        FROM de_tai dt
        JOIN nguoi_dung gv ON gv.ma_nd = dt.ma_gv
        WHERE dt.hoc_ky = ?
        ORDER BY dt.trang_thai, dt.ten_de_tai
        """,
        (HOC_KY,),
    ).fetchall()

    giang_vien = sorted({t["ten_gv"] for t in topics})
    mine = dang_ky_hieu_luc(session["ma_nd"])

    filtered = []
    for t in topics:
        if q and q not in t["ten_de_tai"].lower() and q not in t["ten_gv"].lower():
            continue
        if gv_filter and t["ten_gv"] != gv_filter:
            continue
        con_cho = t["so_luong_da_dk"] < t["so_luong_toi_da"] and t["trang_thai"] == "MO"
        if slot_filter == "con_cho" and not con_cho:
            continue
        filtered.append(t)

    return render_template(
        "de_tai.html",
        topics=filtered,
        giang_vien=giang_vien,
        mine=mine,
        q=request.args.get("q") or "",
        gv_filter=gv_filter,
        slot_filter=slot_filter,
        hoc_ky=HOC_KY,
        user=current_user(),
    )


@app.route("/de-tai/<int:ma_dt>")
@login_required("SV")
def chi_tiet_de_tai(ma_dt: int):
    topic = get_db().execute(
        """
        SELECT dt.*, gv.ho_ten AS ten_gv
        FROM de_tai dt
        JOIN nguoi_dung gv ON gv.ma_nd = dt.ma_gv
        WHERE dt.ma_dt = ?
        """,
        (ma_dt,),
    ).fetchone()
    if not topic:
        flash("Khong tim thay de tai.", "error")
        return redirect(url_for("danh_sach_de_tai"))
    members = get_db().execute(
        """
        SELECT nd.ho_ten, nd.ma_so, dk.ngay_dang_ky
        FROM dang_ky dk
        JOIN nguoi_dung nd ON nd.ma_nd = dk.ma_sv
        WHERE dk.ma_dt = ? AND dk.trang_thai = 'HIEU_LUC'
        ORDER BY dk.ngay_dang_ky
        """,
        (ma_dt,),
    ).fetchall()
    return render_template(
        "chi_tiet.html",
        topic=topic,
        members=members,
        mine=dang_ky_hieu_luc(session["ma_nd"]),
        user=current_user(),
        hoc_ky=HOC_KY,
    )


@app.route("/de-tai/<int:ma_dt>/dang-ky", methods=["POST"])
@login_required("SV")
def dang_ky_de_tai(ma_dt: int):
    db = get_db()
    try:
        db.execute("BEGIN IMMEDIATE")
        existing = db.execute(
            "SELECT * FROM dang_ky WHERE ma_sv = ? AND trang_thai = 'HIEU_LUC'",
            (session["ma_nd"],),
        ).fetchone()
        if existing:
            db.rollback()
            flash("Ban da dang ky mot de tai trong hoc ky nay.", "error")
            return redirect(url_for("de_tai_cua_toi"))

        topic = db.execute(
            "SELECT * FROM de_tai WHERE ma_dt = ?", (ma_dt,)
        ).fetchone()
        if not topic:
            db.rollback()
            flash("Khong tim thay de tai.", "error")
            return redirect(url_for("danh_sach_de_tai"))

        if topic["trang_thai"] != "MO" or topic["so_luong_da_dk"] >= topic["so_luong_toi_da"]:
            db.rollback()
            flash("De tai vua du so luong, vui long chon de tai khac.", "error")
            return redirect(url_for("danh_sach_de_tai"))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "INSERT INTO dang_ky(ma_dt, ma_sv, ngay_dang_ky, trang_thai) VALUES (?,?,?, 'HIEU_LUC')",
            (ma_dt, session["ma_nd"], now),
        )
        new_count = topic["so_luong_da_dk"] + 1
        new_status = "DAY" if new_count >= topic["so_luong_toi_da"] else "MO"
        db.execute(
            "UPDATE de_tai SET so_luong_da_dk = ?, trang_thai = ? WHERE ma_dt = ?",
            (new_count, new_status, ma_dt),
        )
        db.commit()
        flash("Dang ky thanh cong de tai: " + topic["ten_de_tai"], "ok")
        return redirect(url_for("de_tai_cua_toi"))
    except sqlite3.IntegrityError:
        db.rollback()
        flash("Ban da dang ky mot de tai trong hoc ky nay.", "error")
        return redirect(url_for("de_tai_cua_toi"))
    except Exception:
        db.rollback()
        flash("Khong gui duoc yeu cau, thu lai.", "error")
        return redirect(url_for("danh_sach_de_tai"))


@app.route("/de-tai-cua-toi")
@login_required()
def de_tai_cua_toi():
    user = current_user()
    db = get_db()
    if user["vai_tro"] == "SV":
        mine = dang_ky_hieu_luc(user["ma_nd"])
        topic = None
        members = []
        if mine:
            topic = db.execute(
                """
                SELECT dt.*, gv.ho_ten AS ten_gv
                FROM de_tai dt JOIN nguoi_dung gv ON gv.ma_nd = dt.ma_gv
                WHERE dt.ma_dt = ?
                """,
                (mine["ma_dt"],),
            ).fetchone()
            members = db.execute(
                """
                SELECT nd.ho_ten, nd.ma_so, dk.ngay_dang_ky
                FROM dang_ky dk JOIN nguoi_dung nd ON nd.ma_nd = dk.ma_sv
                WHERE dk.ma_dt = ? AND dk.trang_thai = 'HIEU_LUC'
                ORDER BY dk.ngay_dang_ky
                """,
                (mine["ma_dt"],),
            ).fetchall()
        return render_template(
            "de_tai_cua_toi.html",
            user=user,
            topic=topic,
            mine=mine,
            members=members,
            hoc_ky=HOC_KY,
        )

    topics = db.execute(
        """
        SELECT dt.*,
               (SELECT COUNT(*) FROM dang_ky dk
                 WHERE dk.ma_dt = dt.ma_dt AND dk.trang_thai = 'HIEU_LUC') AS so_sv
        FROM de_tai dt
        WHERE dt.ma_gv = ?
        ORDER BY dt.ten_de_tai
        """,
        (user["ma_nd"],),
    ).fetchall()
    return render_template(
        "gv_de_tai.html",
        user=user,
        topics=topics,
        hoc_ky=HOC_KY,
    )


@app.context_processor
def inject_globals():
    return {"hoc_ky": HOC_KY}


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
