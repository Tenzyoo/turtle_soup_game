# 海龟汤游戏模型微调项目

微调小型语言模型，使其作为海龟汤游戏主持人，提供可控、逻辑正确的回复。

## 项目简介

海龟汤（情境猜谜）是一种推理游戏：玩家通过"是/否"问题逐步还原故事真相。本项目通过微调语言模型，构建双Agent协作系统，实现智能游戏主持人。

### 核心问题

直接使用语言模型存在问题：
- 回复不可控、输出无关内容
- 剧透答案
- 判断逻辑错误
- 幻觉问题

### 解决方案：双Agent架构

| Agent | 职责 | 实现 |
|-------|------|------|
| Agent 1 | 逻辑判断（是/否/接近了/不相关/揭晓） | 阿里云Qwen API |
| Agent 2 | 回复生成（语气风格+引导） | 本地微调模型 |

职责分离：强模型做逻辑推理，小模型只学回复风格。

## 技术栈

- **前端**: React + Vite
- **后端**: Flask
- **模型**: Qwen（微调）
- **微调框架**: LLaMA-Factory

## 项目结构

```
puzzle/
├── frontend/                # 前端应用
│   ├── src/
│   │   ├── pages/          # 页面组件
│   │   ├── components/     # 通用组件
│   │   └── App.jsx
│   └── package.json
├── backend/                 # 后端服务
│   ├── app.py              # Flask 主应用
│   ├── agents/             # Agent 模块
│   │   ├── logic_agent.py  # Agent 1: 逻辑判断
│   │   └── reply_agent.py  # Agent 2: 回复生成
│   ├── data/               # 谜题数据
│   └── requirements.txt
├── turtle_soup_model.py     # 微调模型调用封装
├── turtle_soup.json         # 谜题数据源
├── train_data.jsonl         # 训练数据
├── personal.json            # 玩家性格系统
├── task_plan.md             # 任务进度跟踪
└── progress.md              # 开发日志
```

## 快速开始

### 1. 配置 API 密钥

```bash
cd backend
cp config.example.py config.py
# 编辑 config.py，填入你的阿里云 DashScope API 密钥
```

### 2. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 3. 启动服务

```bash
# 后端 (端口 5001)
cd backend
python app.py

# 前端 (端口 5174)
cd frontend
npm run dev
```

### 4. 访问应用

打开浏览器访问 `http://localhost:5174`

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/topics` | GET | 获取所有主题 |
| `/api/puzzles/<topic_id>` | GET | 获取主题下谜题列表 |
| `/api/puzzle/<puzzle_id>` | GET | 获取谜题详情 |
| `/api/chat` | POST | 对话接口（双Agent协同） |
| `/api/hint/<puzzle_id>` | GET | 获取提示 |
| `/api/reveal/<puzzle_id>` | GET | 揭示答案 |

### 对话接口示例

```json
POST /api/chat
{
  "puzzle_id": "001",
  "question": "他是自杀的吗？",
  "history": []
}

Response:
{
  "judgement": "否",
  "reply": "不是自杀，再想想。",
  "is_revealed": false
}
```

## 输出格式

模型输出采用 JSON 结构化格式：

```json
{
  "judgement": "是|否|接近了|不相关|揭晓",
  "reply": "简短引导回复"
}
```

## 玩家性格系统

基于两个维度定义9种玩家人格：

**推理风格**：逻辑 → 中立 → 混乱
**探索风格**：谨慎 → 中立 → 突击

示例：
- `lawful_cautious` - 地毯式搜查官
- `chaotic_aggressive` - 赌徒侦探
- `neutral_neutral` - 均衡游侠

详见 `personal.json`。

## 当前状态

| 服务 | 状态 |
|------|------|
| 后端 Flask | ✅ 运行中 |
| 前端 Vite | ✅ 运行中 |
| Agent 1 (Qwen API) | ✅ 正常 |
| Agent 2 (本地模型) | ⚠️ 输出解析问题 |

### 已知问题

Agent 2 本地模型输出包含多余角色标记，正在优化解析逻辑。

## 开发进度

- [x] 阶段1：架构设计
- [x] 阶段2：数据格式设计
- [ ] 阶段3：数据集准备（进行中）
- [ ] 阶段4：模型微调
- [ ] 阶段5：推理部署
- [x] 阶段6：Web应用开发

## License

MIT