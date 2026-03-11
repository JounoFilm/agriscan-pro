"""
AgriScan Pro - Claude Vision API 解析モジュール
仕様書のプロンプトテンプレートに基づく5つの解析機能
"""

import anthropic
import base64
import json
import os
from datetime import datetime


class AgriScanAnalyzer:
    """Claude Vision APIを使った圃場画像解析クラス"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception:
                self.client = None

    @property
    def is_available(self):
        return self.client is not None

    # ===========================================================
    # 季節別 警戒対象リスト（福岡県防除暦準拠）
    # ===========================================================
    SEASONAL_PEST_LIST = {
        6: """【6月の警戒対象】
- 縞葉枯病（ヒメトビウンカ媒介）
- 除草効果の確認（ノビエ、コナギ、ホタルイ）""",

        7: """【7月前半の警戒対象】
- 葉いもち（梅雨期が最も危険）
- ウンカ類の飛来（トビイロウンカ、セジロウンカ）
- 紋枯病の初発
【7月後半の警戒対象】
- 葉いもちの進展
- ウンカ類の増殖（坪枯れの初期兆候に注意）
- 紋枯病の進展
- コブノメイガの発生""",

        8: """【8月前半の警戒対象】
- 穂いもち（出穂7日前の防除が必要）
- 稲こうじ病
- ウンカ類の坪枯れ拡大
【8月後半の警戒対象（最も重要な時期）】
- 斑点米カメムシ類（イネカメムシ、クモヘリカメムシ、ミナミアオカメムシ）
  ※穂揃期とその7〜10日後の2回防除が効果的
- 穂いもち
- ウンカ類""",

        9: """【9月の警戒対象】
- カメムシ類の継続被害
- 倒伏の確認
- 収穫適期の判定"""
    }

    # ===========================================================
    # プロンプト生成
    # ===========================================================

    def _get_seasonal_list(self, month):
        """月ごとの警戒対象リストを取得"""
        return self.SEASONAL_PEST_LIST.get(month, "【通年の警戒対象】\n- 全般的な生育状態の確認")

    def build_disease_pest_prompt(self, metadata):
        """モジュール①: 病害虫診断プロンプト"""
        month = datetime.strptime(metadata.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').month
        seasonal_list = self._get_seasonal_list(month)

        return f"""あなたは九州・福岡県の水稲栽培に特化した農業AI解析の専門家です。
福岡県病害虫防除所の発表情報に準拠した判定を行います。

以下の空撮画像を分析し、病害虫の兆候を検出してください。

【撮影条件】
- 撮影日: {metadata.get('date', '不明')}
- 圃場所在地: 福岡県朝倉郡筑前町{metadata.get('area', '')}
- 品種: {metadata.get('variety', '不明')}
  ※筑前町の主要品種: 夢つくし、元気つくし、ひのひかり
- 移植日: {metadata.get('transplant_date', '不明')}
- 現在の生育ステージ: {metadata.get('stage', '不明')}
- 直近7日間の天候: {metadata.get('weather_7days', '不明')}
- 直近の気温: 最高{metadata.get('max_temp', '不明')}℃ / 最低{metadata.get('min_temp', '不明')}℃
- 撮影高度: {metadata.get('altitude', '不明')}m
- 使用カメラ: {metadata.get('camera', '不明')}

{seasonal_list}

【病害の判定基準】
■ いもち病（葉いもち）
- 視覚特徴: 紡錘形（先形）の病斑。中央灰白色、周囲褐色、最外縁黄褐色
- サイズ: 1〜3cm
- 発生パターン: 連陰天が続いた後に急増。淡い緑の圃場で発生しやすい
- 混同しやすい症状: 葉先枯れ（生理障害）、ごま葉枯病

■ いもち病（穂いもち）
- 視覚特徴: 穂首の褐変、白穂（穂全体が白く枯れる）
- 混同しやすい症状: ニカメイチュウの白穂（食入好の有無で区別）

■ 紋枯病
- 視覚特徴: 元株の葉鞘に雲形〜不正形の病斑。褐色〜灰白色
- 発生パターン: 密植・多肥の圃場、高温多湿時に進展

■ もみ枯細菌病
- 視覚特徴: 穂の籾が褐色〜暗褐色に変色
- 発生パターン: 出穂後の高温年に多発

■ 稲こうじ病
- 視覚特徴: 穂の籾にオレンジ色〜暗緑色〜黒色の球状の塊（5〜15mm）
- 非常に特徴的な外観のため、確認できれば確信度は高い

■ 縞葉枯病
- 視覚特徴: 葉に白〜黄白色の縞模様（葉脈に沿った条状退緑）
- 九州では専用防除マニュアルが存在するほど重要

【害虫被害の判定基準】
■ ウンカ類の坪枯れ（最重要ターゲット）
- 視覚特徴: 圃場内に円形〜不正形の黄変→褐変→死枯パッチ
- 進行パターン: 初期は小さな黄化（直径1〜2m）→急速に拡大（数日で10m以上）
- 高高度（30m以上）から最も検出しやすい
- 早期発見が被害拡大防止のカギ

■ カメムシ類
- イネカメムシ: 体長10〜12mm、褐色。穂に群がる
- クモヘリカメムシ: 体長15mm、細長い、緑色に褐色筋
- ミナミアオカメムシ: 体長12〜16mm、鮮やかな緑色の盾形
- 低高度（10m以下）でのみ虫体を確認可能

■ コブノメイガ
- 視覚特徴: 葉が縦に巻かれ、内側が白化
- 多発時: 圃場全体が白っぽく見える

■ ニカメイチュウ
- 視覚特徴: しんがれ（心葉の死枯）、しろ穂（穂の白化）
- 穂いもちの白穂との区別: 茎に食入好と虫糞があればニカメイチュウ

【出力形式】
JSONフォーマットで以下を返してください:
```json
{{
  "detections": [
    {{
      "id": "D001",
      "category": "disease または pest",
      "name": "病害虫名（日本語）",
      "name_scientific": "学名",
      "confidence": 0-100の整数,
      "confidence_level": "高確信(80-100) / 中確信(50-79) / 低確信(0-49)",
      "affected_area_ratio": 0.0-100.0,
      "severity": "軽度 / 中度 / 重度",
      "visual_evidence": "画像から読み取った根拠の説明",
      "differential_diagnosis": "鑑別診断（似た症状との区別点）",
      "recommendation": "推奨対処法",
      "urgency": "即時対応 / 1週間以内 / 次回散布時 / 経過観察",
      "recommended_pesticide": "推奨農薬名（福岡県防除暦準拠）"
    }}
  ],
  "overall_health_score": 0-100,
  "overall_assessment": "良好 / 注意 / 要対処 / 緊急",
  "field_notes": "その他の観察事項",
  "next_inspection_recommendation": "次回撮影の推奨時期と注意点"
}}
```

【重要な注意事項】
- 確信度50%未満の場合は必ず「要現地確認」と明記すること
- いもち病とニカメイチュウの白穂の区別は低高度画像がないと困難。その場合は両方を候補として挙げること
- ウンカの坪枯れは早期発見が極めて重要。疑わしい黄変は見逃さず報告すること
- 複数の病害虫が同時発生している可能性を常に考慮すること"""

    def build_weed_prompt(self, metadata):
        """モジュール③: 雑草密度マップ用プロンプト"""
        return f"""あなたは九州の水田雑草に精通した農業AI解析の専門家です。

以下の圃場の空撮画像（高度30〜50m）を分析し、雑草の密度と分布を評価してください。

【撮影条件】
- 撮影日: {metadata.get('date', '不明')}
- 圃場所在地: 福岡県朝倉郡筑前町
- 品種: {metadata.get('variety', '不明')}

【九州の水田で問題になる主な雑草】
ノビエ（ヒエ類）: 最も一般的。稲に似た外観だが葉色がやや淡い
コナギ: 水面付近に繁茂。ハート形の葉
ホタルイ: 直立する茎。群生する
オモダカ: 矢じり形の葉。大型
クログワイ: 地下茎で広がる。根絶が困難

【密度レベル色コード基準】
低（問題なし）: 雑草被度5%未満 → 経過観察
中（注意）  : 雑草被度5〜15% → 次回除草検討
高（要対処）: 雑草被度15〜30% → 除草散布推奨
極高（緊急）: 雑草被度30%以上 → 即時除草散布

【出力形式】
```json
{{
  "overall_coverage_percent": 数値,
  "status": "良好 / 注意 / 要対処 / 緊急",
  "density_grid": [[数値の2Dグリッド(1=低,2=中,3=高,4=極高)]],
  "weeds_found": [
    {{
      "name": "雑草名",
      "coverage_percent": 数値,
      "status": "低 / 注意 / 要対処",
      "location_description": "分布の説明"
    }}
  ],
  "assessment": "総合評価文",
  "recommendation": "推奨対処"
}}
```"""

    def build_infrastructure_prompt(self, metadata):
        """モジュール④: 畦畔・水路チェック用プロンプト"""
        return f"""あなたは農業インフラの専門家です。

以下の圃場周辺の空撮画像（高度30m・斜め撮影）を分析し、畦畔や水路の異常を検出してください。

【検出対象】
異常の種類   | 視覚的特徴                    | 損傷レベル | 推奨対応
-------------|-------------------------------|-----------|--------
畦畔の崩れ   | 法面の形状変化、土砂の流出痕   | 要修繕     | 修繕事業工の手配
畦畔の浸食   | 細い溝状の削れ                | 要注意     | 次回整備時に補修
水路の詰まり | 水面の停滞、藻類の繁茂         | 要清掃     | 水路清掃の実施
モグラ被害   | 畦畔表面の隆起                | 要注意     | 漏水確認・補修
獣害痕      | イノシシの掘り返し痕            | 次第       | 電気柵の点検・強化

【出力形式】
```json
{{
  "issues": [
    {{
      "type": "異常の種類",
      "location": "場所の説明",
      "severity": "要修繕 / 要注意 / 要清掃",
      "description": "状態の説明",
      "recommendation": "推奨対応",
      "icon": "適切な絵文字"
    }}
  ],
  "overall_status": "良好 / 要注意 / 要修繕",
  "notes": "その他の観察事項"
}}
```"""

    def build_spray_quality_prompt(self, metadata):
        """モジュール⑤: 散布品質評価プロンプト"""
        return f"""あなたはドローン散布の品質評価の専門家です。

以下の散布直後の圃場空撮画像を分析し、散布の均一性と品質を評価してください。

【評価基準】
- 散布ムラの有無（未散布エリアの検出）
- 散布の均一性
- 端部・畦畔際の散布状態

【出力形式】
```json
{{
  "spray_quality_score": 0-100,
  "uniformity": "均一 / やや不均一 / 不均一",
  "missed_areas": [
    {{
      "location": "未散布エリアの位置",
      "estimated_area_m2": 数値
    }}
  ],
  "assessment": "評価文",
  "recommendation": "改善提案"
}}
```"""

    # ===========================================================
    # 解析実行
    # ===========================================================

    def _encode_image(self, image_path):
        """画像をbase64エンコード"""
        with open(image_path, 'rb') as f:
            return base64.standard_b64encode(f.read()).decode('utf-8')

    def _get_media_type(self, image_path):
        """ファイル拡張子からメディアタイプを判定"""
        ext = os.path.splitext(image_path)[1].lower()
        types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
        }
        return types.get(ext, 'image/jpeg')

    def _call_claude(self, prompt, image_paths, model="claude-sonnet-4-20250514"):
        """Claude Vision APIを呼び出す"""
        if not self.is_available:
            return None

        # 画像コンテンツの構築
        content = []
        for img_path in image_paths:
            image_data = self._encode_image(img_path)
            media_type = self._get_media_type(img_path)
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data
                }
            })

        content.append({
            "type": "text",
            "text": prompt
        })

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Claude API error: {e}")
            return None

    def _parse_json_response(self, response_text):
        """Claude応答からJSONを抽出"""
        if not response_text:
            return None
        try:
            # ```json ... ``` ブロックの抽出を試みる
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0].strip()
            else:
                # 先頭の { から最後の } までを抽出
                start = response_text.index('{')
                end = response_text.rindex('}') + 1
                json_str = response_text[start:end]
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError, IndexError) as e:
            print(f"JSON parse error: {e}")
            print(f"Raw response: {response_text[:500]}")
            return None

    def analyze_disease_pest(self, image_paths, metadata):
        """モジュール①: 病害虫診断を実行"""
        prompt = self.build_disease_pest_prompt(metadata)
        response = self._call_claude(prompt, image_paths)
        result = self._parse_json_response(response)

        if result:
            # アイコンの付与
            icon_map = {
                'いもち': '🍂', 'ウンカ': '🦗', 'カメムシ': '🐛',
                '紋枯': '🍄', 'もみ枯': '🌾', '稲こうじ': '🟠',
                '縞葉枯': '🌿', 'コブノメイガ': '🐛', 'ニカメイチュウ': '🐛'
            }
            for d in result.get('detections', []):
                d['icon'] = '🔬'
                for key, icon in icon_map.items():
                    if key in d.get('name', ''):
                        d['icon'] = icon
                        break
            return result

        return None

    def analyze_weed(self, image_paths, metadata):
        """モジュール③: 雑草密度解析を実行"""
        prompt = self.build_weed_prompt(metadata)
        response = self._call_claude(prompt, image_paths)
        return self._parse_json_response(response)

    def analyze_infrastructure(self, image_paths, metadata):
        """モジュール④: 畦畔・水路チェックを実行"""
        prompt = self.build_infrastructure_prompt(metadata)
        response = self._call_claude(prompt, image_paths)
        return self._parse_json_response(response)

    def analyze_spray_quality(self, image_paths, metadata):
        """モジュール⑤: 散布品質評価を実行"""
        prompt = self.build_spray_quality_prompt(metadata)
        response = self._call_claude(prompt, image_paths)
        return self._parse_json_response(response)

    def calculate_overall_score(self, disease_result, weed_result, infra_result):
        """5つのモジュールの結果から総合スコアを算出"""
        scores = {}

        # 病害虫スコア
        if disease_result:
            health = disease_result.get('overall_health_score', 70)
            scores['disease'] = health
        else:
            scores['disease'] = 70

        # 雑草スコア
        if weed_result:
            coverage = weed_result.get('overall_coverage_percent', 5)
            if coverage < 5:
                scores['weed'] = 95
            elif coverage < 15:
                scores['weed'] = 75
            elif coverage < 30:
                scores['weed'] = 50
            else:
                scores['weed'] = 25
        else:
            scores['weed'] = 80

        # インフラスコア
        if infra_result:
            issues = len(infra_result.get('issues', []))
            scores['infra'] = max(50, 100 - issues * 15)
        else:
            scores['infra'] = 85

        # 散布スコア（デフォルト）
        scores['spray'] = 90

        # 総合スコア（各モジュールの加重平均）
        weights = {'disease': 0.35, 'weed': 0.2, 'infra': 0.15, 'spray': 0.15, 'health': 0.15}
        scores['health'] = int(
            scores['disease'] * 0.4 +
            scores['weed'] * 0.3 +
            scores['infra'] * 0.3
        )

        overall = int(
            scores['disease'] * weights['disease'] +
            scores['weed'] * weights['weed'] +
            scores['infra'] * weights['infra'] +
            scores['spray'] * weights['spray'] +
            scores['health'] * weights['health']
        )

        # 評価ラベル
        if overall >= 80:
            assessment = '良好'
            assessment_class = 'good'
        elif overall >= 60:
            assessment = '注意'
            assessment_class = 'caution'
        elif overall >= 40:
            assessment = '要対処'
            assessment_class = 'action'
        else:
            assessment = '緊急'
            assessment_class = 'urgent'

        return {
            'score': overall,
            'assessment': assessment,
            'assessmentClass': assessment_class,
            'modules': {
                'disease': {'score': scores['disease'], 'label': '病害虫', 'status': 'ok' if scores['disease'] >= 75 else 'warn' if scores['disease'] >= 50 else 'danger'},
                'weed': {'score': scores['weed'], 'label': '雑草管理', 'status': 'ok' if scores['weed'] >= 75 else 'warn' if scores['weed'] >= 50 else 'danger'},
                'infra': {'score': scores['infra'], 'label': '畦畔・水路', 'status': 'ok' if scores['infra'] >= 75 else 'warn' if scores['infra'] >= 50 else 'danger'},
                'spray': {'score': scores['spray'], 'label': '散布実績', 'status': 'ok'},
                'health': {'score': scores['health'], 'label': '総合健康', 'status': 'ok' if scores['health'] >= 75 else 'warn' if scores['health'] >= 50 else 'danger'},
            }
        }

    def run_full_analysis(self, image_paths, metadata):
        """全モジュールを実行して統合結果を返す"""
        disease_result = self.analyze_disease_pest(image_paths, metadata)
        weed_result = self.analyze_weed(image_paths, metadata)
        infra_result = self.analyze_infrastructure(image_paths, metadata)

        overall = self.calculate_overall_score(disease_result, weed_result, infra_result)

        # アラート生成
        alerts = self._generate_alerts(disease_result, weed_result, infra_result)

        # 次のアクション生成
        next_actions = self._generate_next_actions(disease_result, weed_result, infra_result)

        return {
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata,
            'overallScore': overall,
            'detections': disease_result.get('detections', []) if disease_result else [],
            'weedDensity': weed_result if weed_result else {},
            'infrastructure': infra_result.get('issues', []) if infra_result else [],
            'alerts': alerts,
            'nextActions': next_actions,
            'field_notes': disease_result.get('field_notes', '') if disease_result else '',
            'next_inspection': disease_result.get('next_inspection_recommendation', '') if disease_result else ''
        }

    def _generate_alerts(self, disease_result, weed_result, infra_result):
        """検出結果からアラートを自動生成"""
        alerts = []
        alert_id = 1

        if disease_result:
            for d in disease_result.get('detections', []):
                if d.get('urgency') == '即時対応':
                    alert_type = 'urgent'
                elif d.get('urgency') == '1週間以内':
                    alert_type = 'warning'
                else:
                    alert_type = 'info'

                alerts.append({
                    'id': f'A{alert_id:03d}',
                    'type': alert_type,
                    'title': f"{'【緊急】' if alert_type == 'urgent' else ''}{d.get('name', '')}を検出",
                    'description': d.get('visual_evidence', ''),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'module': '病害虫診断'
                })
                alert_id += 1

        if infra_result:
            for issue in infra_result.get('issues', []):
                alerts.append({
                    'id': f'A{alert_id:03d}',
                    'type': 'info',
                    'title': issue.get('type', ''),
                    'description': issue.get('description', ''),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'module': '畦畔・水路'
                })
                alert_id += 1

        return alerts

    def _generate_next_actions(self, disease_result, weed_result, infra_result):
        """次のアクション推奨リストを生成"""
        actions = []

        if disease_result:
            for d in disease_result.get('detections', []):
                priority_map = {
                    '即時対応': '緊急',
                    '1週間以内': '高',
                    '次回散布時': '中',
                    '経過観察': '低'
                }
                actions.append({
                    'priority': priority_map.get(d.get('urgency', ''), '低'),
                    'action': d.get('recommendation', ''),
                    'deadline': d.get('urgency', '経過観察')
                })

        return sorted(actions, key=lambda x: ['緊急', '高', '中', '低'].index(x['priority']))
