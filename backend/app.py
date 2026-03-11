"""
AgriScan Pro - Flask APIサーバー
圃場画像のAI解析バックエンド
"""

import os
import json
import uuid
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from analyzer import AgriScanAnalyzer
from database import init_db, seed_demo_fields, get_all_fields, get_field, \
    save_analysis, get_all_analyses, get_analysis, save_image_record, create_field

# ============================================================
# アプリケーション初期化
# ============================================================

app = Flask(__name__, static_folder='../') 
CORS(app)

# アップロード設定
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'tiff', 'tif', 'webp', 'gif'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# AI解析エンジン初期化
analyzer = AgriScanAnalyzer()

# DB初期化
init_db()
seed_demo_fields()

print("=" * 60)
print("🌾 AgriScan Pro バックエンド起動")
print(f"   Claude API: {'✅ 有効' if analyzer.is_available else '❌ 無効（デモモード）'}")
print(f"   アップロード先: {UPLOAD_FOLDER}")
print("=" * 60)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================
# 静的ファイル（フロントエンド）
# ============================================================

@app.route('/')
def serve_index():
    return send_from_directory('../', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../', path)


# ============================================================
# API: 解析
# ============================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_images():
    """画像をアップロードしてAI解析を実行"""

    # メタデータ取得
    metadata = {
        'field_id': request.form.get('field_id', ''),
        'date': request.form.get('date', datetime.now().strftime('%Y-%m-%d')),
        'variety': request.form.get('variety', '不明'),
        'stage': request.form.get('stage', '不明'),
        'altitude': request.form.get('altitude', '30'),
        'camera': request.form.get('camera', 'DJI AGRAS T70P'),
        'weather_7days': request.form.get('weather_7days', ''),
        'max_temp': request.form.get('max_temp', ''),
        'min_temp': request.form.get('min_temp', ''),
        'transplant_date': request.form.get('transplant_date', ''),
        'area': request.form.get('area', ''),
    }

    # 圃場情報からメタデータを補完
    if metadata['field_id']:
        field = get_field(metadata['field_id'])
        if field:
            metadata['variety'] = metadata['variety'] or field.get('variety', '')
            metadata['transplant_date'] = metadata['transplant_date'] or field.get('transplant_date', '')
            metadata['area'] = field.get('name', '')

    # 画像ファイルの保存
    files = request.files.getlist('images')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': '画像ファイルが必要です'}), 400

    image_paths = []
    saved_filenames = []
    for f in files:
        if f and f.filename and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            # ユニークな名前を付与
            unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_name)
            f.save(filepath)
            image_paths.append(filepath)
            saved_filenames.append(unique_name)

    if not image_paths:
        return jsonify({'error': '有効な画像ファイルがありません。対応形式: JPG, PNG, TIFF'}), 400

    # AI解析の実行
    if analyzer.is_available:
        # --- Claude API モード ---
        try:
            result = analyzer.run_full_analysis(image_paths, metadata)
            mode = 'ai'
        except Exception as e:
            print(f"AI解析エラー: {e}")
            result = _generate_demo_result(metadata)
            mode = 'demo_fallback'
    else:
        # --- デモモード ---
        result = _generate_demo_result(metadata)
        mode = 'demo'

    # DB保存
    analysis_id = save_analysis(
        metadata.get('field_id'),
        metadata,
        result,
        len(image_paths)
    )

    # 画像レコード保存
    for fn, fp in zip(saved_filenames, image_paths):
        save_image_record(analysis_id, fn, fp)

    return jsonify({
        'success': True,
        'analysis_id': analysis_id,
        'mode': mode,
        'result': result
    })


@app.route('/api/analyses', methods=['GET'])
def list_analyses():
    """過去の解析結果一覧"""
    analyses = get_all_analyses()
    return jsonify({'analyses': analyses})


@app.route('/api/analyses/<int:analysis_id>', methods=['GET'])
def get_analysis_detail(analysis_id):
    """特定の解析結果詳細"""
    analysis = get_analysis(analysis_id)
    if not analysis:
        return jsonify({'error': '解析結果が見つかりません'}), 404
    return jsonify({'analysis': analysis})


# ============================================================
# API: 圃場管理
# ============================================================

@app.route('/api/fields', methods=['GET'])
def list_fields():
    """圃場一覧"""
    fields = get_all_fields()
    # フロントエンド互換のフォーマットに変換
    formatted = []
    for f in fields:
        formatted.append({
            'id': f['id'],
            'name': f['name'],
            'farmer': f['farmer'],
            'area_ha': f['area_ha'],
            'variety': f['variety'],
            'transplant_date': f['transplant_date'],
            'location': {'lat': f['lat'], 'lng': f['lng']},
            'stage': f['stage'],
            'health_score': f['health_score'],
            'last_inspection': f['last_inspection'],
            'status': f['status']
        })
    return jsonify({'fields': formatted})


@app.route('/api/fields', methods=['POST'])
def add_field():
    """新しい圃場を追加"""
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': '圃場名は必須です'}), 400

    new_id = create_field(data)
    field = get_field(new_id)

    return jsonify({
        'success': True,
        'field': {
            'id': field['id'],
            'name': field['name'],
            'farmer': field['farmer'],
            'area_ha': field['area_ha'],
            'variety': field['variety'],
            'transplant_date': field['transplant_date'],
            'location': {'lat': field['lat'], 'lng': field['lng']},
            'stage': field['stage'],
            'health_score': field['health_score'],
            'last_inspection': field['last_inspection'],
            'status': field['status']
        }
    }), 201


@app.route('/api/status', methods=['GET'])
def api_status():
    """API稼働状態"""
    return jsonify({
        'status': 'running',
        'ai_available': analyzer.is_available,
        'mode': 'ai' if analyzer.is_available else 'demo',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


# ============================================================
# デモモード用データ生成
# ============================================================

def _generate_demo_result(metadata):
    """Claude APIが利用できない場合のデモ結果"""
    month = datetime.now().month

    # 季節に合わせたリアルなデモデータ
    detections = [
        {
            'id': 'D001',
            'category': 'pest',
            'name': 'トビイロウンカ',
            'name_scientific': 'Nilaparvata lugens',
            'confidence': 85,
            'confidence_level': '高確信',
            'affected_area_ratio': 2.4,
            'severity': '重度',
            'visual_evidence': '圃場南西部に直径2mの黄変→褐変パッチを3箇所確認。典型的な坪枯れの初期段階。',
            'differential_diagnosis': 'ウンカ坪枯れの特徴：円形の黄化パターンが急速に拡大。他の枯れとは進行速度が異なる。',
            'recommendation': 'ジノテフラン粒剤の緊急散布を推奨。被害拡大前の迅速な対応が必要。',
            'urgency': '即時対応',
            'recommended_pesticide': 'スタークル粒剤（ジノテフラン）',
            'icon': '🦗'
        },
        {
            'id': 'D002',
            'category': 'disease',
            'name': '葉いもち',
            'name_scientific': 'Pyricularia oryzae',
            'confidence': 72,
            'confidence_level': '中確信',
            'affected_area_ratio': 0.4,
            'severity': '軽度',
            'visual_evidence': '紡錘形の病斑を複数確認。中央灰白色、周囲褐色、最外縁黄褐色の典型的パターン。',
            'differential_diagnosis': '葉先枯れ（生理障害）と区別。病斑が紡錘形で周辺黄変があればいもちの可能性が高い。',
            'recommendation': '次回散布時にトリシクラゾール系薬剤の追加を検討。経過観察を推奨。',
            'urgency': '1週間以内',
            'recommended_pesticide': 'ビーム粉剤DL（トリシクラゾール）',
            'icon': '🍂'
        },
        {
            'id': 'D003',
            'category': 'pest',
            'name': 'イネカメムシ',
            'name_scientific': 'Lagynotomus elongatus',
            'confidence': 68,
            'confidence_level': '中確信',
            'affected_area_ratio': 0.2,
            'severity': '中度',
            'visual_evidence': '穂に群がる体長10-12mmの虫体を複数確認。斑点米の発生リスクあり。',
            'differential_diagnosis': 'クモヘリカメムシとの区別：体形が卵形であればイネカメムシ。',
            'recommendation': '穂揃期後7-10日の2回防除が効果的。エチプロール系薬剤を推奨。',
            'urgency': '1週間以内',
            'recommended_pesticide': 'キラップ粉剤DL（エチプロール）',
            'icon': '🐛'
        }
    ]

    weed_result = {
        'overall_coverage_percent': 8.5,
        'status': '注意',
        'density_grid': [
            [1,1,2,2,1,1,1,2,1,1],
            [1,2,3,2,1,1,2,2,1,1],
            [1,1,2,1,1,1,1,2,2,1],
            [2,2,3,2,1,1,1,1,1,1],
            [1,2,2,1,1,1,2,3,2,1],
            [1,1,1,1,1,1,1,2,1,1]
        ],
        'weeds_found': [
            {'name': 'ノビエ（ヒエ類）', 'coverage_percent': 4.2, 'status': '注意',
             'location_description': '圃場西側に集中'},
            {'name': 'コナギ', 'coverage_percent': 2.8, 'status': '注意',
             'location_description': '水面付近に散在'},
            {'name': 'ホタルイ', 'coverage_percent': 1.5, 'status': '低',
             'location_description': '畦畔際に少量'}
        ],
        'assessment': '全体的な雑草被覆率は8.5%で注意レベル。圃場西側でノビエの集中繁殖あり。',
        'recommendation': '次回除草剤散布時に西側エリアを重点的に散布推奨。'
    }

    infrastructure = [
        {
            'type': '畦畔の崩れ',
            'location': '圃場南側',
            'severity': '要注意',
            'description': '法面の形状変化、土砂の流出痕を確認',
            'recommendation': '次回整備時に補修を手配',
            'icon': '⚠️'
        },
        {
            'type': '水路の詰まり',
            'location': '上流側',
            'severity': '要清掃',
            'description': '水面の停滞、藻類の繁殖を確認',
            'recommendation': '水路清掃の実施を推奨',
            'icon': '🚰'
        }
    ]

    # スコア計算
    overall_score = analyzer.calculate_overall_score(
        {'overall_health_score': 65, 'detections': detections},
        weed_result,
        {'issues': infrastructure}
    )

    # アラート生成
    alerts = []
    for d in detections:
        if d['urgency'] == '即時対応':
            atype = 'urgent'
        elif d['urgency'] == '1週間以内':
            atype = 'warning'
        else:
            atype = 'info'
        alerts.append({
            'id': f'A{len(alerts)+1:03d}',
            'type': atype,
            'title': f"{'【緊急】' if atype == 'urgent' else ''}{d['name']}を検出",
            'description': d['visual_evidence'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'module': '病害虫診断'
        })

    next_actions = [
        {'priority': '緊急', 'action': 'ジノテフラン粒剤の緊急散布', 'deadline': '即時対応'},
        {'priority': '高', 'action': 'カメムシ防除（穂揃期+7日）', 'deadline': '1週間以内'},
        {'priority': '中', 'action': '葉いもち経過観察撮影', 'deadline': '1週間以内'},
    ]

    return {
        'timestamp': datetime.now().isoformat(),
        'metadata': metadata,
        'overallScore': overall_score,
        'detections': detections,
        'weedDensity': weed_result,
        'infrastructure': infrastructure,
        'alerts': alerts,
        'nextActions': next_actions,
        'field_notes': '【デモモード】Claude APIキーが設定されていないため、サンプル結果を表示しています。環境変数 ANTHROPIC_API_KEY を設定すると実際のAI解析が実行されます。',
        'next_inspection': '5-7日後の経過観察撮影を推奨'
    }


# ============================================================
# メイン
# ============================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
