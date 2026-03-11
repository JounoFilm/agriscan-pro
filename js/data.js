// ============================================
// AgriScan Pro - Demo Data
// サンプルデータ（デモ用）
// ============================================

const DEMO_DATA = {
  // 圃場情報
  fields: [
    {
      id: 'F001',
      name: '下田圃場（A区画）',
      farmer: '田中 太郎',
      area_ha: 1.2,
      variety: 'ひのひかり',
      transplant_date: '2026-06-15',
      location: { lat: 33.4547, lng: 130.6473 },
      stage: '出穂期',
      health_score: 78,
      last_inspection: '2026-08-05',
      status: 'caution'
    },
    {
      id: 'F002',
      name: '上ノ原圃場（B区画）',
      farmer: '田中 太郎',
      area_ha: 0.8,
      variety: '元気つくし',
      transplant_date: '2026-06-10',
      location: { lat: 33.4562, lng: 130.6510 },
      stage: '登熟期',
      health_score: 92,
      last_inspection: '2026-08-05',
      status: 'good'
    },
    {
      id: 'F003',
      name: '中山棚田（C区画）',
      farmer: '佐藤 花子',
      area_ha: 0.5,
      variety: 'ひのひかり',
      transplant_date: '2026-06-20',
      location: { lat: 33.4531, lng: 130.6432 },
      stage: '穂揃期',
      health_score: 45,
      last_inspection: '2026-08-04',
      status: 'action'
    },
    {
      id: 'F004',
      name: '谷口水田（D区画）',
      farmer: '山本 健一',
      area_ha: 2.1,
      variety: '夢つくし',
      transplant_date: '2026-06-12',
      location: { lat: 33.4580, lng: 130.6550 },
      stage: '出穂期',
      health_score: 85,
      last_inspection: '2026-08-05',
      status: 'good'
    },
    {
      id: 'F005',
      name: '大平圃場（E区画）',
      farmer: '鈴木 一郎',
      area_ha: 1.5,
      variety: '元気つくし',
      transplant_date: '2026-06-18',
      location: { lat: 33.4510, lng: 130.6490 },
      stage: '穂揃期',
      health_score: 62,
      last_inspection: '2026-08-03',
      status: 'caution'
    },
    {
      id: 'F006',
      name: '長尾段々畑（F区画）',
      farmer: '佐藤 花子',
      area_ha: 0.3,
      variety: 'ひのひかり',
      transplant_date: '2026-06-22',
      location: { lat: 33.4495, lng: 130.6415 },
      stage: '出穂期',
      health_score: 31,
      last_inspection: '2026-08-05',
      status: 'urgent'
    }
  ],

  // 総合スコア
  overallScore: {
    score: 72,
    assessment: '注意',
    assessmentClass: 'caution',
    trend: -3,
    previousScore: 75,
    modules: {
      disease: { score: 65, label: '病害虫', status: 'warn' },
      weed: { score: 80, label: '雑草管理', status: 'ok' },
      infra: { score: 85, label: '畦畔・水路', status: 'ok' },
      spray: { score: 90, label: '散布実績', status: 'ok' },
      health: { score: 72, label: '総合健康', status: 'warn' }
    }
  },

  // 病害虫検出結果
  detections: [
    {
      id: 'D001',
      category: 'pest',
      name: 'トビイロウンカ',
      name_scientific: 'Nilaparvata lugens',
      confidence: 85,
      confidence_level: '高確信',
      field: 'F003',
      field_name: '中山棚田（C区画）',
      affected_area_m2: 120,
      affected_area_ratio: 2.4,
      severity: '重度',
      visual_evidence: '圃場南西部に直径2mの黄変→褐変パッチを3箇所確認。典型的な坪枯れの初期段階。',
      recommendation: 'ジノテフラン粒剤の緊急散布を推奨。被害拡大前の迅速な対応が必要。',
      urgency: '即時対応',
      recommended_pesticide: 'スタークル粒剤（ジノテフラン）',
      icon: '🦗'
    },
    {
      id: 'D002',
      category: 'disease',
      name: '葉いもち',
      name_scientific: 'Pyricularia oryzae',
      confidence: 72,
      confidence_level: '中確信',
      field: 'F001',
      field_name: '下田圃場（A区画）',
      affected_area_m2: 45,
      affected_area_ratio: 0.4,
      severity: '軽度',
      visual_evidence: '紡錘形の病斑を複数確認。中央灰白色、周囲褐色、最外縁黄褐色の典型的パターン。',
      recommendation: '次回散布時にトリシクラゾール系薬剤の追加を検討。経過観察を推奨。',
      urgency: '1週間以内',
      recommended_pesticide: 'ビーム粉剤DL（トリシクラゾール）',
      icon: '🍂'
    },
    {
      id: 'D003',
      category: 'pest',
      name: 'イネカメムシ',
      name_scientific: 'Lagynotomus elongatus',
      confidence: 68,
      confidence_level: '中確信',
      field: 'F005',
      field_name: '大平圃場（E区画）',
      affected_area_m2: 30,
      affected_area_ratio: 0.2,
      severity: '中度',
      visual_evidence: '穂に群がる体長10-12mmの緑色虫体を複数確認。斑点米の発生リスクあり。',
      recommendation: '穂揃期後7-10日の2回防除が効果的。エチプロール系薬剤を推奨。',
      urgency: '1週間以内',
      recommended_pesticide: 'キラップ粉剤DL（エチプロール）',
      icon: '🐛'
    },
    {
      id: 'D004',
      category: 'disease',
      name: '紋枯病',
      name_scientific: 'Rhizoctonia solani',
      confidence: 58,
      confidence_level: '中確信',
      field: 'F001',
      field_name: '下田圃場（A区画）',
      affected_area_m2: 60,
      affected_area_ratio: 0.5,
      severity: '軽度',
      visual_evidence: '元株の葉鞘に雲形〜不正形の病斑。褐色〜灰白色。密植部で確認。',
      recommendation: '高温多湿が続く場合は進展に注意。次回散布時の防除検討。',
      urgency: '次回散布時',
      recommended_pesticide: 'モンカットフロアブル',
      icon: '🍄'
    },
    {
      id: 'D005',
      category: 'pest',
      name: 'コブノメイガ',
      name_scientific: 'Cnaphalocrocis medinalis',
      confidence: 45,
      confidence_level: '低確信',
      field: 'F004',
      field_name: '谷口水田（D区画）',
      affected_area_m2: 15,
      affected_area_ratio: 0.07,
      severity: '軽度',
      visual_evidence: '葉が縦に巻かれ内側が白化している箇所を数点確認。要現地確認。',
      recommendation: '被害が軽微なため経過観察。被害拡大時はBT剤の散布を検討。',
      urgency: '経過観察',
      recommended_pesticide: '要現地判断',
      icon: '🐛'
    }
  ],

  // 雑草密度データ（10×6グリッド）
  weedDensity: {
    field: 'F001',
    field_name: '下田圃場（A区画）',
    overall_coverage: 8.5,
    status: '注意',
    grid: [
      [1,1,2,2,1,1,1,2,1,1],
      [1,2,3,2,1,1,2,2,1,1],
      [1,1,2,1,1,1,1,2,2,1],
      [2,2,3,2,1,1,1,1,1,1],
      [1,2,2,1,1,1,2,3,2,1],
      [1,1,1,1,1,1,1,2,1,1]
    ],
    weeds_found: [
      { name: 'ノビエ（ヒエ類）', coverage: 4.2, status: '注意' },
      { name: 'コナギ', coverage: 2.8, status: '注意' },
      { name: 'ホタルイ', coverage: 1.5, status: '低' }
    ]
  },

  // 畦畔・水路状態
  infrastructure: [
    {
      type: '畦畔の崩れ',
      location: '下田圃場 南側',
      severity: '要注意',
      description: '法面の形状変化、土砂の流出痕を確認',
      recommendation: '次回整備時に補修を手配',
      icon: '⚠️'
    },
    {
      type: '水路の詰まり',
      location: '中山棚田 上流側',
      severity: '要清掃',
      description: '水面の停滞、藻類の繁殖を確認',
      recommendation: '水路清掃の実施を推奨',
      icon: '🚰'
    },
    {
      type: 'モグラ被害痕',
      location: '大平圃場 東側',
      severity: '要注意',
      description: 'イノシシの掘り返し痕状の跡を確認',
      recommendation: '漏水確認・補修',
      icon: '🕳️'
    }
  ],

  // 散布実績
  sprayRecords: [
    {
      date: '2026-08-05',
      time: '06:30-08:45',
      field: '下田圃場（A区画）・上ノ原圃場（B区画）',
      area_ha: 2.0,
      pesticide: 'スタークル粒剤（ジノテフラン）',
      volume_l: 16,
      drone: 'DJI AGRAS T70P',
      weather: '晴れ 27℃ 風速2m/s 南西',
      operator: '操縦者A',
      status: '完了'
    },
    {
      date: '2026-07-28',
      time: '05:45-07:30',
      field: '全圃場（6区画一斉散布）',
      area_ha: 6.4,
      pesticide: 'ビーム粉剤DL（トリシクラゾール）',
      volume_l: 52,
      drone: 'DJI AGRAS T70P',
      weather: '曇り 25℃ 風速1.5m/s 北東',
      operator: '操縦者A',
      status: '完了'
    },
    {
      date: '2026-07-20',
      time: '06:00-07:15',
      field: '中山棚田（C区画）・大平圃場（E区画）',
      area_ha: 2.0,
      pesticide: 'キラップ粉剤DL（エチプロール）',
      volume_l: 16,
      drone: 'DJI AGRAS T70P',
      weather: '晴れ 30℃ 風速3m/s 南',
      operator: '操縦者B',
      status: '完了'
    },
    {
      date: '2026-07-10',
      time: '06:15-08:00',
      field: '下田圃場（A区画）・谷口水田（D区画）',
      area_ha: 3.3,
      pesticide: '除草剤（バサグラン液剤）',
      volume_l: 26,
      drone: 'DJI AGRAS T70P',
      weather: '曇り 28℃ 風速2m/s 西',
      operator: '操縦者A',
      status: '完了'
    }
  ],

  // アラート
  alerts: [
    {
      id: 'A001',
      type: 'urgent',
      title: '【緊急】ウンカ坪枯れの兆候を検出',
      description: '中山棚田（C区画）南西部で坪枯れ初期段階を確認。早期対応が必要です。',
      field: 'F003',
      timestamp: '2026-08-05 09:30',
      module: '病害虫診断'
    },
    {
      id: 'A002',
      type: 'warning',
      title: '葉いもち病の拡大傾向',
      description: '下田圃場（A区画）で葉いもちの新規発生を確認。前回より病斑数が増加。',
      field: 'F001',
      timestamp: '2026-08-05 09:35',
      module: '病害虫診断'
    },
    {
      id: 'A003',
      type: 'warning',
      title: '斑点米カメムシ防除適期',
      description: '大平圃場（E区画）で穂揃期後7日を迎えます。カメムシ防除の最適時期です。',
      field: 'F005',
      timestamp: '2026-08-05 09:40',
      module: '病害虫診断'
    },
    {
      id: 'A004',
      type: 'info',
      title: '畦畔補修の推奨',
      description: '下田圃場 南側の畦畔で軽微な崩れを確認。次回整備時の対応を推奨します。',
      field: 'F001',
      timestamp: '2026-08-05 09:45',
      module: '畦畔・水路'
    }
  ],

  // 次回推奨アクション
  nextActions: [
    { priority: '緊急', action: 'C区画にジノテフラン粒剤の緊急散布', deadline: '8月6日まで' },
    { priority: '高', action: 'E区画のカメムシ防除（穂揃期+7日）', deadline: '8月8日まで' },
    { priority: '中', action: 'A区画の葉いもち経過観察撮影', deadline: '8月10日まで' },
    { priority: '低', action: '畦畔補修の手配確認', deadline: '次回整備時' }
  ]
};

// Export for use in other modules
if (typeof module !== 'undefined') {
  module.exports = DEMO_DATA;
}
