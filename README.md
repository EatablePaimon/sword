# sword

一个基于 **Aho–Corasick（AC 自动机）** 的敏感词/合规文本扫描服务，提供简单的“是否命中”检测与带位置的详细扫描结果。

项目启动后会从 `./wordlib/` 目录加载词库（多个 `.txt` 文件）。

## 功能

- `POST /check`：快速检测文本是否包含敏感词
- `POST /scan`：扫描并返回命中的词、行号与行内位置

默认监听：`0.0.0.0:8080`

## 接口说明

### `POST /check`

请求 JSON：

```json
{ "text": "要检测的文本" }
```

返回：

- 命中敏感词：

```json
{ "status": "failed" }
```

- 未命中：

```json
{ "status": "clean" }
```

参数错误：

```json
{ "error": "参数'text'缺失或非字符串" }
```

### `POST /scan`

请求 JSON：

```json
{ "text": "要扫描的文本" }
```

返回：

- 命中时：

```json
{
	"status": "failed",
	"matches": [
		{
			"word": "命中的词",
			"line": 1,
			"start_pos": 1,
			"end_pos": 3,
			"source": "来源词库文件名或分类"
		}
	]
}
```

- 未命中时：

```json
{ "status": "clean", "matches": [] }
```

> `start_pos`/`end_pos` 为**行内从 1 开始**的字符位置。

## 本地运行（Python）

建议使用虚拟环境。

```bash
pip install -r requirements.txt
python main.py
```

启动后访问：`http://127.0.0.1:8080`

## Docker 运行

仓库已提供 `Dockerfile`，默认暴露端口 `8080`。

```bash
docker build -t sword:latest .
docker run --rm -p 8080:8080 sword:latest
```

## 请求示例

使用 curl：

```bash
curl -s http://127.0.0.1:8080/check \
	-H 'Content-Type: application/json' \
	-d '{"text":"hello"}'
```

```bash
curl -s http://127.0.0.1:8080/scan \
	-H 'Content-Type: application/json' \
	-d '{"text":"第一行\n第二行"}'
```

## 词库说明

- 词库目录：`wordlib/`
- 词库文件：多个 `.txt`，按行存储词条（具体解析逻辑以 `advancedac.py` 为准）

## 注意事项

- 服务启动时会加载词库：确保容器/运行环境中存在 `wordlib/`。
- 当前实现依赖 `AdvancedAC`（见 `advancedac.py`），如需热加载词库或自定义词库路径，可在此基础上扩展。