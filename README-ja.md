# SWA WASM DuckDB NDJSON ログビューア

Azure App Service のコンソール出力から NDJSON (Newline Delimited JSON) ログを可視化する Static Web App です。

## 概要

このプロジェクトは、[appsvc-console-to-blob](https://github.com/skmkzyk/appsvc-console-to-blob) によって保存された NDJSON ログを分析・可視化する Web ベースのログビューアを提供します。DuckDB WASM を使用してブラウザ上で完結するため、サーバーサイドの処理を必要とせず、高速な SQL クエリを実行できます。

### 主な機能

- **DuckDB WASM 統合**: クライアントサイドで高速な分析クエリを実行
- **ドラッグ＆ドロップアップロード**: NDJSON ログファイルの簡単なアップロード UI
- **SQL クエリインターフェース**: カスタム SQL クエリでログを分析
- **統計ダッシュボード**: ログデータの自動生成統計
- **モダンな UI**: グラデーションデザインを採用したクリーンでレスポンシブなインターフェース
- **バックエンド不要**: すべての処理がブラウザ内で完結
- **Python API (オプション)**: 拡張性のための Azure Functions エンドポイント

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Static Web App (Azure)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  フロントエンド (index.html)                                   │
│  ├─ DuckDB WASM (CDN から取得)                               │
│  ├─ ファイルアップロード UI                                    │
│  ├─ SQL クエリインターフェース                                 │
│  └─ 結果の可視化                                              │
│                                                               │
│  バックエンド API (Python - オプション)                         │
│  ├─ /api/health - ヘルスチェック                             │
│  └─ /api/info - API 情報                                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                             ▲
                             │
                    ユーザーが NDJSON をアップロード
                             │
                             │
┌─────────────────────────────────────────────────────────────┐
│              Azure Blob Storage (オプション)                  │
│  └─ appsvc-console-to-blob からの NDJSON ログ               │
│     └─ フォーマット: YYYY/MM/DD/console.ndjson              │
└─────────────────────────────────────────────────────────────┘
```

## プロジェクト構造

```
.
├── azure.yaml                      # Azure Developer CLI 設定
├── infra/                          # Infrastructure as Code (Bicep)
│   ├── main.bicep                 # メインインフラストラクチャテンプレート
│   ├── main.parameters.json       # デプロイ用パラメータ
│   ├── abbreviations.json         # Azure リソース命名規則
│   └── core/
│       └── host/
│           └── staticwebapp.bicep # Static Web App リソース定義
├── src/                           # アプリケーションソースコード
│   ├── index.html                 # メインフロントエンドアプリケーション
│   └── api/                       # Python Azure Functions API
│       ├── function_app.py        # API エンドポイント
│       ├── requirements.txt       # Python 依存関係
│       └── host.json              # Functions ランタイム設定
└── README.md                      # このファイル（英語版）
```

## 技術スタック

### フロントエンド
- **HTML5/CSS3/JavaScript**: コア Web 技術
- **DuckDB WASM**: ブラウザ内 SQL データベースによるログ分析
  - バージョン: 1.28.0 (jsDelivr CDN から取得)
  - クライアントサイドで NDJSON データに対する SQL クエリを実行
- **モダン CSS**: グラデーション背景、Flexbox/Grid レイアウト

### バックエンド (オプション)
- **Python 3.11+**: Azure Functions ランタイム
- **Azure Functions**: サーバーレス API エンドポイント
  - ヘルスチェックエンドポイント
  - 情報エンドポイント

### インフラストラクチャ
- **Azure Static Web Apps**: ホスティングプラットフォーム
  - 無料枠が利用可能
  - GitHub Actions による組み込み CI/CD
  - グローバル CDN 配信
- **Bicep**: Infrastructure as Code
- **Azure Developer CLI (azd)**: デプロイ自動化

## クイックスタート

### 前提条件

- [Azure Developer CLI (azd)](https://learn.microsoft.com/ja-jp/azure/developer/azure-developer-cli/install-azd)
- [Azure サブスクリプション](https://azure.microsoft.com/ja-jp/free/)
- [Git](https://git-scm.com/downloads)
- モダンな Web ブラウザ (Chrome, Firefox, Edge, Safari)

### ローカル開発

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/skmkzyk/swa-wasm-duckdb-ndjson.git
   cd swa-wasm-duckdb-ndjson
   ```

2. **シンプルな HTTP サーバーでローカルテスト**
   ```bash
   # Python を使用する場合
   cd src
   python -m http.server 8000
   
   # または Node.js を使用する場合
   npx http-server src -p 8000
   ```

3. **ブラウザで開く**
   ```
   http://localhost:8000
   ```

### Azure へのデプロイ

すべてを 1 つのコマンドでデプロイ:

```bash
azd up
```

これにより以下が実行されます:
1. Azure サブスクリプションとロケーションの入力を求められます
2. Azure リソースグループを作成
3. Static Web App のインフラストラクチャをデプロイ
4. アプリケーションをビルドしてデプロイ
5. デプロイされた URL を出力

### 手動デプロイ手順

手動デプロイを希望する場合:

1. **azd 環境の初期化**
   ```bash
   azd init
   ```

2. **インフラストラクチャのプロビジョニング**
   ```bash
   azd provision
   ```

3. **アプリケーションのデプロイ**
   ```bash
   azd deploy
   ```

## ログビューアの使い方

### 1. NDJSON ログの読み込み

**オプション A: ローカルファイルのアップロード**
- **ドラッグ＆ドロップ**: `.ndjson`、`.jsonl`、または `.gz` ファイルをアップロード領域にドラッグ
- **クリックして参照**: アップロード領域をクリックしてコンピュータからファイルを選択

**オプション B: Azure Blob Storage から読み込み**
- URL 入力フィールドに完全な blob URL を入力
- 平文および gzip 圧縮ファイル（`.ndjson.gz`）の両方に対応
- 例: `https://storageaccount.blob.core.windows.net/logs-container/y=2026/m=01/d=10/h=08/m=00/p=00/part-*.ndjson.gz`
- 「Load from URL」をクリックまたは Enter キーを押す

### 2. サポートされているログフォーマット

ビューアは、各行が有効な JSON オブジェクトである NDJSON フォーマットを想定しています:

```json
{"time": "2026-01-10T12:34:56Z", "level": "INFO", "message": "Request received", "host": "example.com"}
{"time": "2026-01-10T12:34:57Z", "level": "ERROR", "message": "Connection timeout", "host": "example.com"}
{"time": "2026-01-10T12:34:58Z", "level": "INFO", "message": "Response sent", "host": "example.com"}
```

このフォーマットは [appsvc-console-to-blob](https://github.com/skmkzyk/appsvc-console-to-blob) によって自動生成されます。

### 3. ログのクエリ

SQL を使用してログをクエリします。クエリ例:

**最新 100 件を取得:**
```sql
SELECT * FROM logs ORDER BY time DESC LIMIT 100
```

**レベル別にログをカウント:**
```sql
SELECT level, COUNT(*) as count 
FROM logs 
GROUP BY level 
ORDER BY count DESC
```

**すべてのエラーを検索:**
```sql
SELECT * FROM logs 
WHERE level = 'ERROR' 
ORDER BY time DESC
```

**ホスト別に分析:**
```sql
SELECT host, COUNT(*) as count 
FROM logs 
GROUP BY host 
ORDER BY count DESC
```

**時間ベースの分析:**
```sql
SELECT DATE_TRUNC('hour', CAST(time AS TIMESTAMP)) as hour, 
       COUNT(*) as count 
FROM logs 
GROUP BY hour 
ORDER BY hour DESC
```

### 4. 結果の表示

結果はスクロール可能なテーブルに表示されます:
- ログデータからの列ヘッダー
- ソート・検索可能（SQL 経由）
- 統計サマリー（総レコード数、フィールド数など）

## API エンドポイント

Python API はオプションのバックエンドエンドポイントを提供します:

### GET /api/health
API が実行中であることを確認するヘルスチェックエンドポイント。

**レスポンス:**
```json
{
  "status": "healthy",
  "message": "NDJSON Log Viewer API is running",
  "version": "1.0.0"
}
```

### GET /api/info
アプリケーションとサンプルクエリに関する情報。

**レスポンス:**
```json
{
  "name": "NDJSON Log Viewer",
  "description": "Visualize NDJSON logs from App Service using DuckDB WASM",
  "features": [...],
  "supported_formats": [".ndjson", ".jsonl"],
  "example_queries": [...]
}
```

## ユースケース

1. **App Service ログ分析**: Azure App Service のコンソールログを分析
2. **エラー調査**: エラーログを素早くクエリしてフィルタリング
3. **パフォーマンス分析**: 時間帯別にログを集計
4. **ホストベースの分析**: FQDN やホスト別にログをグループ化
5. **カスタムメトリクス**: カスタム集計のための SQL クエリを記述

## セキュリティに関する考慮事項

- **クライアントサイド処理**: すべてのログデータはブラウザ内に留まります
- **サーバーアップロードなし**: ファイルはローカルで処理され、サーバーにアップロードされません
- **CORS**: Azure Static Web Apps 用に適切に設定
- **HTTPS**: Azure デプロイ時に自動的に有効化

## 開発

### サンプルデータでのテスト

テスト用のサンプル NDJSON ファイルを作成:

```bash
cat > sample.ndjson << 'EOF'
{"time": "2026-01-10T10:00:00Z", "level": "INFO", "message": "Application started", "host": "app1.example.com"}
{"time": "2026-01-10T10:00:01Z", "level": "INFO", "message": "Request received", "host": "app1.example.com"}
{"time": "2026-01-10T10:00:02Z", "level": "ERROR", "message": "Database connection failed", "host": "app1.example.com"}
{"time": "2026-01-10T10:00:03Z", "level": "WARN", "message": "Retry attempt 1", "host": "app1.example.com"}
{"time": "2026-01-10T10:00:05Z", "level": "INFO", "message": "Connection established", "host": "app1.example.com"}
{"time": "2026-01-10T10:01:00Z", "level": "INFO", "message": "Processing request", "host": "app2.example.com"}
{"time": "2026-01-10T10:01:30Z", "level": "ERROR", "message": "Timeout occurred", "host": "app2.example.com"}
EOF
```

### アプリケーションの拡張

**新しい Python API エンドポイントを追加:**
1. `src/api/function_app.py` を編集
2. `@app.route()` で新しいルートを追加
3. `azd deploy` でデプロイ

**UI のカスタマイズ:**
1. `src/index.html` を編集
2. `<style>` セクションで CSS を変更
3. `<script>` モジュールで JavaScript を更新

**インフラストラクチャの変更:**
1. `infra/` ディレクトリ内の Bicep ファイルを編集
2. `azd provision` でプロビジョニング

## 環境変数

ローカル API 開発用に `src/api/local.settings.json` を作成:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

## CI/CD

Azure Static Web Apps は、`azd up` 経由でデプロイすると、GitHub Actions の CI/CD を自動的にセットアップします。ワークフロー:

1. main ブランチへのプッシュでトリガー
2. アプリケーションのビルド
3. Azure Static Web Apps へのデプロイ
4. Python API を Azure Functions としてデプロイ

## トラブルシューティング

### 問題: "Failed to initialize DuckDB"
- **解決方法**: WebAssembly サポートのあるモダンなブラウザを使用していることを確認
- ブラウザコンソールで詳細なエラーを確認

### 問題: "File parsing failed"
- **解決方法**: ファイルが有効な NDJSON（1 行に 1 つの JSON オブジェクト）であることを確認
- 各行が有効な JSON であることを確認

### 問題: "Query execution failed"
- **解決方法**: SQL 構文を確認
- 列名がデータと一致することを確認
- テーブル名は常に `logs` であることを覚えておく

### 問題: "azd up fails"
- **解決方法**: Azure CLI と azd がインストールされていることを確認
- ログインしていることを確認: `azd auth login`
- Azure サブスクリプションを確認: `az account show`

## 参考資料

- [DuckDB WASM ドキュメント](https://duckdb.org/docs/api/wasm)
- [Azure Static Web Apps ドキュメント](https://learn.microsoft.com/ja-jp/azure/static-web-apps/)
- [Azure Developer CLI ドキュメント](https://learn.microsoft.com/ja-jp/azure/developer/azure-developer-cli/)
- [App Service Console to Blob](https://github.com/skmkzyk/appsvc-console-to-blob)
- [NDJSON フォーマット仕様](http://ndjson.org/)

## ライセンス

MIT License

## コントリビューション

コントリビューションを歓迎します！お気軽にプルリクエストを送信してください。

## 作者

- **skmkzyk** - 初期作業と App Service ログ収集

## 謝辞

- 優れた WASM 実装を提供してくれた DuckDB チーム
- ホスティングプラットフォームを提供してくれた Azure Static Web Apps チーム
- 診断ログ機能を提供してくれた App Service チーム

---

## 言語 / Languages

- [English (README.md)](./README.md)
- [日本語 (README-ja.md)](./README-ja.md) - このファイル
