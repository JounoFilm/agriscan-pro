"""
AgriScan Pro - SQLite データベースモジュール
解析結果・圃場情報の永続化
"""

import sqlite3
import json
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), 'agriscan.db')


def get_db():
    """データベース接続を取得"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """データベースの初期化（テーブル作成）"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS fields (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            farmer TEXT,
            area_ha REAL,
            variety TEXT,
            transplant_date TEXT,
            lat REAL,
            lng REAL,
            stage TEXT,
            health_score INTEGER DEFAULT 0,
            last_inspection TEXT,
            status TEXT DEFAULT 'good',
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_id TEXT,
            analysis_date TEXT DEFAULT (datetime('now', 'localtime')),
            metadata_json TEXT,
            result_json TEXT,
            overall_score INTEGER,
            assessment TEXT,
            image_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (field_id) REFERENCES fields(id)
        );

        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            filename TEXT,
            filepath TEXT,
            uploaded_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        );
    """)

    conn.commit()
    conn.close()


def seed_demo_fields():
    """デモ用の圃場データを投入"""
    conn = get_db()
    cursor = conn.cursor()

    # 既にデータがあればスキップ
    count = cursor.execute("SELECT COUNT(*) FROM fields").fetchone()[0]
    if count > 0:
        conn.close()
        return

    fields = [
        ('F001', '下田圃場（A区画）', '田中 太郎', 1.2, 'ひのひかり', '2026-06-15', 33.4547, 130.6473, '出穂期', 78, '2026-08-05', 'caution'),
        ('F002', '上ノ原圃場（B区画）', '田中 太郎', 0.8, '元気つくし', '2026-06-10', 33.4562, 130.6510, '登熟期', 92, '2026-08-05', 'good'),
        ('F003', '中山棚田（C区画）', '佐藤 花子', 0.5, 'ひのひかり', '2026-06-20', 33.4531, 130.6432, '穂揃期', 45, '2026-08-04', 'action'),
        ('F004', '谷口水田（D区画）', '山本 健一', 2.1, '夢つくし', '2026-06-12', 33.4580, 130.6550, '出穂期', 85, '2026-08-05', 'good'),
        ('F005', '大平圃場（E区画）', '鈴木 一郎', 1.5, '元気つくし', '2026-06-18', 33.4510, 130.6490, '穂揃期', 62, '2026-08-03', 'caution'),
        ('F006', '長尾段々畑（F区画）', '佐藤 花子', 0.3, 'ひのひかり', '2026-06-22', 33.4495, 130.6415, '出穂期', 31, '2026-08-05', 'urgent'),
    ]

    cursor.executemany(
        "INSERT INTO fields (id, name, farmer, area_ha, variety, transplant_date, lat, lng, stage, health_score, last_inspection, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        fields
    )

    conn.commit()
    conn.close()


# === CRUD操作 ===

def get_all_fields():
    """全圃場を取得"""
    conn = get_db()
    rows = conn.execute("SELECT * FROM fields ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_field(field_id):
    """特定の圃場を取得"""
    conn = get_db()
    row = conn.execute("SELECT * FROM fields WHERE id = ?", (field_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_field_score(field_id, score, status):
    """圃場の健康スコアと状態を更新"""
    conn = get_db()
    conn.execute(
        "UPDATE fields SET health_score = ?, status = ?, last_inspection = ?, updated_at = ? WHERE id = ?",
        (score, status, datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), field_id)
    )
    conn.commit()
    conn.close()


def save_analysis(field_id, metadata, result, image_count):
    """解析結果を保存"""
    conn = get_db()
    cursor = conn.cursor()

    overall = result.get('overallScore', {})
    score = overall.get('score', 0) if isinstance(overall, dict) else 0
    assessment = overall.get('assessment', '不明') if isinstance(overall, dict) else '不明'

    cursor.execute(
        """INSERT INTO analyses (field_id, metadata_json, result_json, overall_score, assessment, image_count)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (field_id, json.dumps(metadata, ensure_ascii=False),
         json.dumps(result, ensure_ascii=False), score, assessment, image_count)
    )

    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # 圃場のスコアも更新
    if field_id and score > 0:
        if score >= 80:
            status = 'good'
        elif score >= 60:
            status = 'caution'
        elif score >= 40:
            status = 'action'
        else:
            status = 'urgent'
        update_field_score(field_id, score, status)

    return analysis_id


def get_all_analyses():
    """全解析結果を取得（新しい順）"""
    conn = get_db()
    rows = conn.execute(
        """SELECT a.*, f.name as field_name
           FROM analyses a
           LEFT JOIN fields f ON a.field_id = f.id
           ORDER BY a.analysis_date DESC
           LIMIT 50"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_analysis(analysis_id):
    """特定の解析結果を取得"""
    conn = get_db()
    row = conn.execute(
        """SELECT a.*, f.name as field_name
           FROM analyses a
           LEFT JOIN fields f ON a.field_id = f.id
           WHERE a.id = ?""",
        (analysis_id,)
    ).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d['result'] = json.loads(d['result_json']) if d['result_json'] else {}
        d['metadata'] = json.loads(d['metadata_json']) if d['metadata_json'] else {}
        return d
    return None


def save_image_record(analysis_id, filename, filepath):
    """画像レコードを保存"""
    conn = get_db()
    conn.execute(
        "INSERT INTO images (analysis_id, filename, filepath) VALUES (?, ?, ?)",
        (analysis_id, filename, filepath)
    )
    conn.commit()
    conn.close()


def create_field(data):
    """新しい圃場を作成"""
    conn = get_db()
    cursor = conn.cursor()

    # 次のIDを生成
    max_id = cursor.execute("SELECT id FROM fields ORDER BY id DESC LIMIT 1").fetchone()
    if max_id:
        num = int(max_id[0].replace('F', '')) + 1
    else:
        num = 1
    new_id = f'F{num:03d}'

    cursor.execute(
        """INSERT INTO fields (id, name, farmer, area_ha, variety, transplant_date, lat, lng, stage, health_score, last_inspection, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 'good')""",
        (new_id, data.get('name', ''), data.get('farmer', ''),
         float(data.get('area_ha', 0)), data.get('variety', ''),
         data.get('transplant_date', ''),
         float(data.get('lat', 0)), float(data.get('lng', 0)),
         data.get('stage', '移植前'),
         datetime.now().strftime('%Y-%m-%d'))
    )
    conn.commit()
    conn.close()
    return new_id

