#!/bin/bash
# =============================================
# AgriScan Pro セットアップスクリプト
# 新しいPCでこのスクリプトを実行するだけで環境構築完了
# =============================================

echo ""
echo "🌾 =================================="
echo "   AgriScan Pro セットアップ"
echo "   =================================="
echo ""

# Python確認
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3が見つかりません"
    echo "   brew install python3 でインストールしてください"
    exit 1
fi

PYTHON_VER=$(python3 --version 2>&1)
echo "✅ $PYTHON_VER を検出"

# 仮想環境の作成
echo ""
echo "📦 Python仮想環境を作成中..."
if [ -d "backend/venv" ]; then
    echo "   既に存在します。スキップ。"
else
    python3 -m venv backend/venv
    echo "   ✅ backend/venv を作成しました"
fi

# 仮想環境を有効化
source backend/venv/bin/activate

# パッケージインストール
echo ""
echo "📥 依存パッケージをインストール中..."
pip install -r backend/requirements.txt --quiet
echo "   ✅ Flask, Anthropic, Pillow 等をインストール完了"

# uploadsディレクトリ確認
mkdir -p backend/uploads

echo ""
echo "🎉 =================================="
echo "   セットアップ完了！"
echo "   =================================="
echo ""
echo "   起動方法:"
echo "   ────────────────────────"
echo "   source backend/venv/bin/activate"
echo "   python backend/app.py"
echo ""
echo "   ブラウザで http://localhost:5001/ を開いてください"
echo ""
echo "   ※ AI解析を有効にするには:"
echo "   export ANTHROPIC_API_KEY=sk-ant-api03-xxxxx"
echo "   python backend/app.py"
echo ""
