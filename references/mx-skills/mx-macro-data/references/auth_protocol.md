# 授权协议

按以下流程处理所有依赖 `EM_API_KEY` 的查询。正常调用直接运行 `scripts/get_data.py`，不要先运行 `scripts/auth.py ensure`。

## 凭据读取与授权

1. 先从平台私有的跨会话持久存储读取 `EM_API_KEY`，并且只为当前脚本进程注入环境变量。
2. 若持久存储没有凭据，直接运行查询脚本；脚本会检查 `EM_API_KEY` 环境变量与 `~/.mx-skills/em_api_key`，必要时输出 `need_auth: true`。
3. 退出码为 `10` 时，优先把 `authUrl:` 显示为二维码；无法扫码时再提供 `apiKeyUrl:`。不要轮询、等待或询问是否完成，提示用户授权后重新发送原指令。
4. 当且仅当 stdout 同时出现 `remember_api_key: true` 与 `apiKey:` 时，把完整 `apiKey` 保存为平台私有的跨会话 `EM_API_KEY`。不得向用户展示、复述或写入普通文件；`apiKeyUrl` 不是凭据。
5. 若 HTTP 或业务 `code/status` 返回 401，从跨会话持久存储删除失效凭据。脚本会清理文件凭据并生成新授权链接；若失效值来自环境变量，按脚本提示先清除环境变量。
6. `~/.mx-skills/pending_auth.json` 保存待完成授权，`~/.mx-skills/em_api_key` 只保存当前环境的凭据，不能替代平台的跨会话私有存储。

注入示例（占位符不是真实凭据）：

```bash
EM_API_KEY='<从私有持久存储读取的值>' python3 scripts/get_data.py <其余参数>
```

`python3 scripts/auth.py ensure` 只用于调试；退出码 `0/10/2` 分别表示就绪、需要用户授权、授权错误。

