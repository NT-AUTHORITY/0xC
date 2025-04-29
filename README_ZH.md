# 0xC 聊天 API

一个使用 Python Flask 为 0xC（聊天）项目构建的简单聊天 API。

[English Documentation](README.md)

## 功能特点

- 聊天消息的 RESTful API
- 消息的创建、读取和删除操作
- 使用 JWT 令牌和刷新令牌的用户认证
- 使用 JSON 文件进行持久化数据存储
- JSON 格式的响应
- 通过环境变量进行配置（可自定义端口、主机等）

## 项目结构

```
0xC/
├── app.py              # 主应用程序文件
├── auth.py             # 认证中间件
├── api_key.py          # API Key 中间件
├── auth_routes.py      # 认证路由
├── config.py           # 配置设置
├── env.py              # 环境变量
├── json_storage.py     # JSON 文件存储模块
├── models.py           # 数据模型
├── routes.py           # API 路由
├── requirements.txt    # 依赖项
├── test_api.py         # 单元测试
├── test_client.py      # API 测试客户端示例
├── .env.example        # 环境变量示例
├── data/               # JSON 数据文件目录（运行时创建）
│   ├── users.json      # 用户数据
│   ├── messages.json   # 消息数据
│   └── tokens.json     # 刷新令牌数据
├── README.md           # 英文文档
└── README_ZH.md        # 中文文档
```

## API 端点

### 消息端点

- `GET /api/messages` - 获取当前用户可查看的所有消息（需要认证）
- `POST /api/messages` - 发送新消息，可选择指定接收者（需要认证）
- `GET /api/messages/<message_id>` - 获取特定消息（需要认证和权限）
- `DELETE /api/messages/<message_id>` - 删除消息（需要认证和所有权）
- `GET /api/messages/me` - 获取已认证用户发送的所有消息（需要认证）

注意：用户可以查看以下消息：
1. 用户发送的消息
2. 发送给用户的消息
3. 公开消息（未指定接收者）

### 认证端点

- `POST /api/auth/register` - 注册新用户
- `POST /api/auth/login` - 登录并获取访问令牌和刷新令牌
- `POST /api/auth/refresh` - 使用刷新令牌刷新访问令牌
- `POST /api/auth/logout` - 登出并使刷新令牌失效
- `GET /api/auth/token-info` - 获取当前令牌的信息

## API 安全机制

### API Key 认证

当 `SECRET_KEY_ENABLED=1` 时，所有 API 请求都需要在请求头中包含 API Key：

```
X-API-Key: your-secret-key-here
```

这是一个全局安全机制，独立于用户认证系统。它可以用于：
- 限制只有授权的客户端应用程序可以访问 API
- 为整个 API 添加一层额外的安全保护
- 在开发或测试环境中禁用（设置 `SECRET_KEY_ENABLED=0`）

### JWT 认证

JWT（JSON Web Token）用于用户级别的认证和授权：
- 用户登录后获取访问令牌（Access Token）和刷新令牌（Refresh Token）
- 访问令牌用于访问受保护的 API 端点
- 刷新令牌用于在访问令牌过期后获取新的访问令牌

两种认证机制可以同时使用，提供多层次的安全保护。

## API 响应格式

所有 API 响应都遵循一致的 JSON 格式，包含以下字段：

### 成功响应

成功的响应包含 `status` 字段（值为 "success"）和相关数据：

```json
{
  "status": "success",
  "message": "操作成功的描述信息（可选）",
  "data": {
    // 返回的数据对象（针对单个资源）
  }
}
```

或者对于返回集合的端点：

```json
{
  "status": "success",
  "messages": [
    // 返回的数据对象数组
  ]
}
```

### 错误响应

错误响应包含 `status` 字段（值为 "error"）和错误信息：

```json
{
  "status": "error",
  "message": "错误描述信息"
}
```

#### 错误响应示例

**认证失败（401 Unauthorized）**：

```json
{
  "status": "error",
  "message": "Authentication token is missing"
}
```

**资源不存在（404 Not Found）**：

```json
{
  "status": "error",
  "message": "Message with ID 550e8400-e29b-41d4-a716-446655440001 not found"
}
```

**请求参数错误（400 Bad Request）**：

```json
{
  "status": "error",
  "message": "Missing required field: content"
}
```

**权限错误（401 Unauthorized）**：

```json
{
  "status": "error",
  "message": "Message with ID 550e8400-e29b-41d4-a716-446655440001 not found or you do not have permission to delete it"
}
```

### HTTP 状态码

API 使用标准 HTTP 状态码：

- `200 OK` - 请求成功
- `201 Created` - 资源创建成功
- `400 Bad Request` - 请求参数错误
- `401 Unauthorized` - 认证失败或缺少认证信息
- `404 Not Found` - 资源不存在
- `500 Internal Server Error` - 服务器内部错误

## 认证流程

0xC Chat API 使用基于 JWT 的认证系统，包括访问令牌（Access Token）和刷新令牌（Refresh Token）。

### 认证流程图

```
┌─────────┐                                                  ┌─────────┐
│         │                                                  │         │
│  客户端  │                                                  │  服务器  │
│         │                                                  │         │
└────┬────┘                                                  └────┬────┘
     │                                                            │
     │  1. 注册用户 POST /api/auth/register                        │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  2. 返回用户信息                                            │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
     │  3. 登录 POST /api/auth/login                              │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  4. 返回访问令牌和刷新令牌                                   │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
     │  5. 使用访问令牌访问受保护资源                                │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  6. 返回受保护资源                                          │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
     │  7. 访问令牌过期                                            │
     │                                                            │
     │  8. 使用刷新令牌获取新的访问令牌 POST /api/auth/refresh       │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  9. 返回新的访问令牌                                         │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
     │  10. 使用新的访问令牌访问受保护资源                           │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  11. 返回受保护资源                                         │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
     │  12. 登出 POST /api/auth/logout                            │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  13. 确认登出成功                                           │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
```

### 认证说明

1. **访问令牌（Access Token）**：
   - 短期有效（默认 15 分钟）
   - 用于访问受保护的 API 端点
   - 在请求头中使用 `Authorization: Bearer <token>` 格式
   - 包含 `refresh_at` 时间戳，指示客户端应该在何时刷新令牌（默认在过期前 10 分钟）

2. **刷新令牌（Refresh Token）**：
   - 长期有效（默认 30 天）
   - 用于在访问令牌过期后获取新的访问令牌
   - 存储在客户端，需要安全保存

3. **认证流程**：
   - 用户注册并登录获取令牌
   - 使用访问令牌访问受保护资源
   - 当当前时间达到 `refresh_at` 时间戳时，客户端应主动刷新令牌（在令牌完全过期前）
   - 如果访问令牌已过期，使用刷新令牌获取新的访问令牌
   - 继续使用新的访问令牌访问受保护资源
   - 用户登出时，刷新令牌被服务器端废弃

## 安装和设置

1. 克隆仓库：
   ```
   git clone https://github.com/NT_AUTHORITY/0xC.git
   cd 0xC
   ```

2. 创建虚拟环境（可选但推荐）：
   ```
   python -m venv venv
   source venv/bin/activate  # 在 Windows 上: venv\Scripts\activate
   ```

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

4. 配置环境变量（可选）：
   ```
   cp .env.example .env
   # 编辑 .env 文件，根据需要修改设置
   ```

5. 运行应用程序：
   ```
   python app.py
   ```

API 默认将在 `http://localhost:5000` 上可用，或者在您的环境变量中指定的主机和端口上可用。

### 自定义端口

您可以通过多种方式在不同的端口上运行应用程序：

1. **直接使用环境变量**：
   ```bash
   # 在 Linux/Mac 上
   PORT=8080 python app.py

   # 在 Windows 上 (PowerShell)
   $env:PORT=8080; python app.py

   # 在 Windows 上 (命令提示符)
   set PORT=8080 && python app.py
   ```

2. **使用 .env 文件**：
   创建或编辑您的 `.env` 文件并添加：
   ```
   PORT=8080
   ```
   然后正常运行应用程序：
   ```
   python app.py
   ```

应用程序现在将在 `http://localhost:8080` 上可用。

## 测试

### 单元测试

使用以下命令运行单元测试：
```
python test_api.py
```

### 测试客户端

提供了一个示例客户端，用于演示如何以编程方式与 API 交互：

```
python test_client.py
```

测试客户端演示了：
- 用户注册和登录
- 令牌管理（包括自动令牌刷新）
- 发送和检索消息
- 错误处理

您可以使用命令行参数自定义 API URL 和提供 API 密钥：

```
python test_client.py --url http://localhost:8080 --api-key your-secret-key
```

要求：
- `requests` 库：`pip install requests`

## 使用示例

### 认证

#### 注册新用户

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key-here" \
  -d '{"username": "user1", "password": "password123", "email": "user1@example.com"}'
```

> 注意：只有在 `SECRET_KEY_ENABLED=1` 时才需要 `X-API-Key` 请求头

**响应：**

```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "user1",
    "email": "user1@example.com",
    "created_at": "2023-09-15T14:30:45.123456"
  }
}
```

#### 登录并获取令牌

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'
```

**响应：**

```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "user1",
      "email": "user1@example.com",
      "created_at": "2023-09-15T14:30:45.123456"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

#### 刷新访问令牌

```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

**响应：**

```json
{
  "status": "success",
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

#### 登出

```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

**响应：**

```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

#### 令牌信息

```bash
curl -X GET http://localhost:5000/api/auth/token-info \
  -H "Authorization: Bearer your-access-token"
```

**响应：**

```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "user1",
      "email": "user1@example.com",
      "created_at": "2023-09-15T14:30:45.123456"
    },
    "token_info": {
      "type": "access",
      "issued_at": 1694789445,
      "expires_at": 1694790345,
      "refresh_at": 1694790045
    }
  }
}
```

### 消息

#### 发送公开消息（需要认证）

```bash
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-API-Key: your-secret-key-here" \
  -d '{"content": "Hello, world!"}'
```

#### 发送私信给特定用户（需要认证）

```bash
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-API-Key: your-secret-key-here" \
  -d '{"content": "Hello, this is a private message!", "recipient_id": "user-id-here"}'
```

> 注意：
> - `Authorization` 请求头用于用户认证（JWT）
> - `X-API-Key` 请求头用于 API 认证（只有在 `SECRET_KEY_ENABLED=1` 时才需要）
> - 公开消息（没有 recipient_id）对所有用户可见
> - 私信（有 recipient_id）只对发送者和接收者可见

**响应：**

```json
{
  "status": "success",
  "message": "Message created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "user1",
    "content": "Hello, world!",
    "timestamp": "2023-09-15T14:35:12.654321"
  }
}
```

#### 获取您的消息（需要认证）

```bash
curl -X GET http://localhost:5000/api/messages \
  -H "Authorization: Bearer your-access-token"
```

**响应：**

```json
{
  "status": "success",
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "user1",
      "content": "Hello, world!",
      "timestamp": "2023-09-15T14:35:12.654321"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "user_id": "550e8400-e29b-41d4-a716-446655440003",
      "username": "user2",
      "content": "Hi there!",
      "timestamp": "2023-09-15T14:36:05.123456"
    }
  ]
}
```

#### 获取我的消息（需要认证）

```bash
curl -X GET http://localhost:5000/api/messages/me \
  -H "Authorization: Bearer your-access-token"
```

**响应：**

```json
{
  "status": "success",
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "user1",
      "content": "Hello, world!",
      "timestamp": "2023-09-15T14:35:12.654321"
    }
  ]
}
```

#### 获取特定消息（需要认证和所有权）

```bash
curl -X GET http://localhost:5000/api/messages/550e8400-e29b-41d4-a716-446655440001 \
  -H "Authorization: Bearer your-access-token"
```

注意：只有当认证用户是消息的发送者时，此操作才会成功。

**响应：**

```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "user1",
    "content": "Hello, world!",
    "timestamp": "2023-09-15T14:35:12.654321"
  }
}
```

#### 删除消息（需要认证，需要所有权）

```bash
curl -X DELETE http://localhost:5000/api/messages/550e8400-e29b-41d4-a716-446655440001 \
  -H "Authorization: Bearer your-access-token"
```

**响应：**

```json
{
  "status": "success",
  "message": "Message with ID 550e8400-e29b-41d4-a716-446655440001 deleted successfully"
}
```

## 环境变量

应用程序使用环境变量进行配置。您可以在 `.env` 文件中或直接在环境中设置这些变量。

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| FLASK_ENV | 应用程序环境 | development |
| FLASK_DEBUG | 启用调试模式 | 1 (True) |
| HOST | 服务器主机 | 0.0.0.0 |
| PORT | 服务器端口 | 5000 |
| SECRET_KEY | 安全密钥 | dev-key-for-0xC-chat |
| SECRET_KEY_ENABLED | 如果为 true，所有 API 操作都需要密钥（X-API-Key 请求头） | 0 (False) |
| JWT_SECRET_KEY | JWT 令牌的密钥（用于签名和验证用户认证令牌） | jwt-secret-key-for-0xC-chat |
| REGISTER_ENABLED | 如果为 false，禁用用户注册 | 1 (True) |
| ACCESS_TOKEN_EXPIRES | 访问令牌过期前的时间（分钟） | 15 |
| TOKEN_REFRESH_SECONDS | 令牌应该刷新的时间（秒） | 600 |
| REFRESH_TOKEN_EXPIRES | 刷新令牌过期前的时间（天） | 30 |
| API_PREFIX | API 端点前缀 | /api |
| LOG_LEVEL | 日志级别 | INFO |
| DATA_DIR | 存储 JSON 数据文件的目录 | data |
| CORS_ORIGINS | 允许的 CORS 来源 | * |
| RATE_LIMIT_ENABLED | 启用速率限制 | 0 (False) |
| RATE_LIMIT | 每分钟速率限制 | 100 |
| MAX_MESSAGE_LENGTH | 最大消息长度 | 1000 |

## 未来改进

- 实现聊天室或用户之间的直接消息传递
- 添加消息编辑功能
- 实现实时消息传递（WebSockets）
- 添加用户资料管理
- 添加密码重置功能
- 实现基于角色的访问控制
- 添加电子邮件验证
- 为认证端点实现速率限制
- 添加数据库支持作为替代存储选项
