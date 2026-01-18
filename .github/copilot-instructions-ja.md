# swa-wasm-duckdb-ndjson のための GitHub Copilot 指示書

このドキュメントは、NDJSON ログビューアプロジェクトで作業する GitHub Copilot と開発者のためのガイダンスを提供します。

## プロジェクト概要

これは、DuckDB WASM を使用して NDJSON (Newline Delimited JSON) ログを可視化する Static Web App です。このアプリケーションは、Azure App Service のコンソール出力からのログ、特に [appsvc-console-to-blob](https://github.com/skmkzyk/appsvc-console-to-blob) によって保存されたログと連携するように設計されています。

## アーキテクチャ原則

### コアデザイン
- **フロントエンド優先**: すべてのログ処理は DuckDB WASM を使用してブラウザ内で行われます
- **データアップロードなし**: ファイルはクライアントサイドで処理され、サーバーにアップロードされません
- **Python API**: オプションのバックエンドはメタデータとヘルスエンドポイントのみを提供
- **Infrastructure as Code**: すべての Azure リソースは Bicep テンプレートで定義

### 技術スタック
- **フロントエンド**: DuckDB WASM (1.28.0) を使用した純粋な HTML/CSS/JavaScript
- **バックエンド**: Azure Functions v4 を使用した Python 3.11+
- **インフラストラクチャ**: Azure Static Web Apps (無料枠対応)
- **デプロイ**: Azure Developer CLI (azd)

## コードスタイルと規約

### Python コード
- PEP 8 スタイルガイドラインに従う
- 適切な場所で型ヒントを使用
- API 関数をシンプルで集中したものに保つ
- デコレータを使用した Azure Functions v4 プログラミングモデルを使用
- 常に適切な HTTP ステータスコードでエラーを優雅に処理

例:
```python
@app.route(route="endpoint", methods=["GET"])
def endpoint_handler(req: func.HttpRequest) -> func.HttpResponse:
    """エンドポイントを説明する明確な docstring"""
    try:
        # 実装
        return func.HttpResponse(json.dumps(data), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse("Error message", status_code=500)
```

### JavaScript コード
- モダンな ES6+ 機能を使用（async/await、アロー関数、テンプレートリテラル）
- 関数を小さく集中させる
- 説明的な変数名を使用
- 常に try/catch で Promise を処理
- デフォルトで const を使用、必要な場合は let、var は使用しない

### HTML/CSS
- グラデーションカラースキームを維持（プライマリ: #667eea、セカンダリ: #764ba2）
- レスポンシブデザイン原則を維持
- セマンティック HTML5 要素を使用
- アクセシビリティを維持（ARIA ラベル、キーボードナビゲーション）
- CSS は index.html 内にインラインで記述（シンプルさのための単一ファイルアプリ）

### Bicep インフラストラクチャ
- パラメータ化されたテンプレートを使用
- abbreviations.json の Azure リソース略語に従う
- 複雑なリソースには説明的なコメントを含める
- 環境識別のためにリソースタグを使用

## ファイル構成

```
.
├── .github/
│   ├── copilot-instructions.md       # 英語版指示書
│   └── copilot-instructions-ja.md    # このファイル（日本語版）
├── infra/                             # Infrastructure as Code
│   ├── main.bicep                    # メインテンプレート（軽々しく変更しない）
│   ├── main.parameters.json          # デプロイパラメータ
│   ├── abbreviations.json            # Azure 命名規則
│   └── core/host/
│       └── staticwebapp.bicep        # SWA リソース定義
├── src/
│   ├── index.html                    # メインアプリケーション（オールインワン）
│   ├── staticwebapp.config.json      # SWA ルーティング設定
│   └── api/                          # Python Functions API
│       ├── function_app.py           # API エンドポイント
│       ├── requirements.txt          # Python 依存関係
│       └── host.json                 # Functions 設定
├── azure.yaml                         # azd 設定
├── sample.ndjson                      # テストデータ
├── README.md                          # ドキュメント（英語）
└── README-ja.md                       # ドキュメント（日本語）
```

## 開発ガイドライン

### 機能追加時

1. **フロントエンド機能**（DuckDB クエリ、UI 改善）:
   - `src/index.html` を変更
   - `python -m http.server 8000` でローカルテスト
   - DuckDB WASM バージョンの互換性を確保
   - 新しいクエリパターンを追加する場合はサンプルクエリセクションを更新
   - sample.ndjson でテスト

2. **バックエンド API エンドポイント**:
   - `src/api/function_app.py` に新しい関数を追加
   - `@app.route()` デコレータで既存のパターンに従う
   - `README.md` の API ドキュメントセクションを更新
   - Azure Functions Core Tools でローカルテスト: `func start`
   - エンドポイントはシンプルに保つ - 複雑なロジックはクライアントサイドで

3. **インフラストラクチャの変更**:
   - `infra/` ディレクトリ内の Bicep テンプレートを変更
   - デプロイ前に `azd provision --preview` でテスト
   - 新しいリソースを追加する場合は `README.md` を更新
   - 新しいリソースのコスト影響を考慮

### テスト要件

**コミット前:**
1. sample.ndjson ファイルでローカルテスト
2. すべてのサンプルクエリが正しく動作することを確認
3. ドラッグ＆ドロップファイルアップロードをテスト
4. 手動ファイル選択をテスト
5. 無効なファイルでのエラー処理を確認
6. ブラウザコンソールでエラーをチェック
7. レスポンシブデザインをテスト（モバイル/タブレット/デスクトップ）

**API 変更の場合:**
1. curl または Postman でエンドポイントをテスト
2. JSON レスポンスが有効であることを確認
3. エラーケースをテスト
4. ログ出力をチェック

### よくあるタスク

#### 新しい SQL サンプルクエリの追加
1. `src/index.html` を開く
2. `.example-queries` セクションを見つける
3. 次のパターンで新しい div を追加:
```html
<div class="example-query" data-query="YOUR SQL HERE">
    <code>クエリの説明</code>
</div>
```

#### 新しい API エンドポイントの追加
1. `src/api/function_app.py` を開く
2. 新しい関数を追加:
```python
@app.route(route="yourroute", methods=["GET", "POST"])
def your_handler(req: func.HttpRequest) -> func.HttpResponse:
    # 実装
    pass
```
3. README.md の API セクションを更新

#### UI の色/テーマの変更
- プライマリグラデーション: `#667eea` から `#764ba2`
- すべての UI 要素で一貫性を保つ
- アクセシビリティのコントラスト比を維持

#### 新しいインフラストラクチャリソースの追加
1. `infra/core/` で Bicep ファイルを作成/変更
2. `infra/main.bicep` から参照
3. 重要な値のために出力を追加
4. 必要に応じて azure.yaml を更新

## DuckDB WASM 仕様

### 重要な制約
- テーブル名は常に `logs`（ハードコード）
- データは `read_json_auto()` を使用して `format='newline_delimited'` で読み込み
- DuckDB WASM バージョンは jsDelivr CDN の 1.28.0 に固定
- すべての SQL はブラウザで実行 - サーバーサイド実行なし

### DuckDB WASM での作業
- ページ読み込み時に一度初期化
- すべてのクエリで接続を再利用
- 非同期操作を適切に処理
- メモリ制限が適用される（ブラウザ依存）
- 大きなファイル（>100MB）はパフォーマンス問題を引き起こす可能性がある

### サンプルクエリパターン
```sql
-- 基本的なフィルタリング
SELECT * FROM logs WHERE record.level = 'Error' LIMIT 100

-- 集計
SELECT fqdn, COUNT(*) as count FROM logs GROUP BY fqdn

-- 時間ベースの分析
SELECT DATE_TRUNC('hour', CAST(time_utc AS TIMESTAMP)) as hour, COUNT(*) 
FROM logs GROUP BY hour ORDER BY hour DESC

-- 複数条件
SELECT * FROM logs 
WHERE record.level IN ('Error', 'Warning') 
  AND fqdn LIKE '%example%'
ORDER BY time_utc DESC
```

## デプロイ

### ローカルテスト
```bash
# フロントエンドのみ
cd src
python -m http.server 8000
# http://localhost:8000 にアクセス

# API あり
cd src/api
func start
# http://localhost:7071 のフロントエンド（または SWA CLI を設定）
```

### Azure デプロイ
```bash
# フルデプロイ
azd up

# インフラストラクチャのみ
azd provision

# コードのみ
azd deploy
```

## 一般的な問題と解決方法

### 問題: DuckDB の初期化に失敗
- ブラウザコンソールで WASM エラーを確認
- CDN アクセス可能性を確認（jsDelivr）
- WASM サポートのあるモダンなブラウザを確認
- CSP（Content Security Policy）制限をチェック

### 問題: ファイルアップロードに失敗
- ファイルが有効な NDJSON（1 行に 1 つの JSON）であることを確認
- ファイルサイズを確認（ブラウザメモリ制限）
- 各行が有効な JSON であることを確認
- ブラウザコンソールで解析エラーを確認

### 問題: クエリが失敗
- テーブル名が `logs` であることを確認
- 列名がデータと一致することを確認
- SQL 構文を確認（DuckDB フレーバー）
- UI のエラーメッセージを確認

### 問題: azd デプロイが失敗
- Azure CLI ログインを確認: `az account show`
- サブスクリプションアクセスを確認
- Bicep テンプレート構文を確認
- リソース名の可用性を確認

## セキュリティに関する考慮事項

### クライアントサイドセキュリティ
- すべてのデータ処理はクライアントサイド（データはブラウザを離れない）
- 静的コンテンツに認証は不要
- API エンドポイントは匿名（公開情報のみに適している）

### 機能追加時
- JavaScript に機密データを保存しない
- ユーザーデータをサーバーサイドで処理するエンドポイントを追加しない
- 本番環境で HTTPS を維持
- API の CORS ベストプラクティスに従う
- すべての入力をクライアントサイドで検証

## パフォーマンスガイドライン

### フロントエンドパフォーマンス
- index.html を単一ファイルとして保持（HTTP/2 フレンドリー）
- DuckDB WASM は CDN を使用（バンドルしない）
- 結果の遅延ロード（テーブルスクロールで既に実装済み）
- デフォルトのクエリ結果を制限（現在: 100 行）

### バックエンドパフォーマンス
- API レスポンスを小さく保つ
- すべての API レスポンスに JSON を使用
- 適切な場所でキャッシングヘッダーを実装
- Azure Functions での重い処理を避ける

## メンテナンス

### 依存関係
- **DuckDB WASM**: https://duckdb.org で四半期ごとに更新をチェック
- **Azure Functions**: 安定版にピン留め
- **Python**: LTS バージョンを使用（現在 3.11+）

### 定期的な更新
1. DuckDB WASM リリースを確認
2. 新しいブラウザバージョンでテスト
3. Azure Static Web Apps プラットフォームの更新をチェック
4. 新機能で README を更新

## AI アシスタンスのベストプラクティス

このプロジェクトで GitHub Copilot または類似ツールを使用する場合:

1. **単一ファイルフロントエンドを維持**: index.html を自己完結型に保つ
2. **ビルドステップを追加しない**: これは意図的にシンプルでビルド不要のプロジェクト
3. **Python のシンプルさを維持**: API は最小限に保つ
4. **既存のパターンに従う**: 一貫性が重要
5. **sample.ndjson でテスト**: 常に変更が動作することを確認
6. **ドキュメントを更新**: README の変更はコード変更に伴う
7. **Azure コストを考慮**: 無料/低コスト階層に固執

## 変更前に問うべき質問

- これは「クライアントサイド優先」の哲学を維持していますか？
- これは不要な複雑さを追加していますか？
- これはビルドステップなしで実行できますか？
- これは sample.ndjson ファイルで動作しますか？
- README はまだ正確ですか？
- これは Static Web Apps の無料枠で動作しますか？
- これは既存のコードスタイルに従っていますか？

## リソース

- [DuckDB WASM ドキュメント](https://duckdb.org/docs/api/wasm)
- [Azure Static Web Apps ドキュメント](https://learn.microsoft.com/ja-jp/azure/static-web-apps/)
- [Azure Functions Python ドキュメント](https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-reference-python)
- [Azure Developer CLI ドキュメント](https://learn.microsoft.com/ja-jp/azure/developer/azure-developer-cli/)
- [NDJSON 仕様](http://ndjson.org/)

## 連絡先

質問や問題については、以下を参照してください:
- このリポジトリの GitHub Issues
- ユーザードキュメントは README.md
- プラットフォーム固有の質問は Azure ドキュメント

---

## 📝 注意事項

この日本語版は開発者が参照するためのものです。GitHub Copilot は英語版の copilot-instructions.md を参照します。
