# pull-android-apk

`pull-android-apk` 是一个 Agent Skill，用于从 Android 设备导出指定应用的主 APK 和全部已安装拆分 APK，并校验包名、版本、签名和 SHA-256。

采用通用 `SKILL.md` 格式，适用于支持 Agent Skills 和本地命令执行的工具，包括 Codex、Claude Code、OpenCode、Cursor。Python 脚本仅使用标准库，无需 MCP 服务。

## 直接从仓库安装到 Codex CLI

在终端运行 Codex 自带的插件安装命令：

```bash
codex plugin marketplace add johnsonconnor97815/pull-android-apk
codex plugin add pull-android-apk@pull-android-apk
```

然后新开一个 Codex 会话，使用 `pull-android-apk`，或直接描述拉取 APK 的需求。用 `codex plugin list` 检查安装状态。该入口需要提供 `codex plugin` 子命令的版本；旧版可使用下方的通用 Skill 安装方式。

## 直接从仓库安装到 Claude Code CLI

在终端运行 Claude Code 自带的安装命令：

```bash
claude plugin marketplace add johnsonconnor97815/pull-android-apk
claude plugin install pull-android-apk@pull-android-apk
```

也可以在 Claude Code 交互会话内执行：

```text
/plugin marketplace add johnsonconnor97815/pull-android-apk
/plugin install pull-android-apk@pull-android-apk
/reload-plugins
```

安装后可调用 `/pull-android-apk:pull-android-apk`，或直接让 Claude 拉取指定包。`claude plugin details pull-android-apk@pull-android-apk` 可以查看它识别到的 Skill。

两套原生安装入口都从这个 GitHub 仓库下载完整 Skill 和脚本，并将 Skill 注册到 Agent 中。仓库已公开，下载时无需 GitHub 身份验证。Android SDK、Java 和设备连接仍按下方运行依赖准备。

## 通过通用 Skill 安装器安装

使用 [Vercel Skills CLI](https://github.com/vercel-labs/skills)：

```bash
npx skills add johnsonconnor97815/pull-android-apk --skill pull-android-apk
```

安装时选择目标 Agent。也可以指定工具并全局安装：

```bash
npx skills add johnsonconnor97815/pull-android-apk \
  --skill pull-android-apk --agent claude-code codex opencode cursor --global
```

不使用 Node.js 时，可直接克隆到目标 Agent 的技能目录。例如 Codex 的用户技能目录：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/johnsonconnor97815/pull-android-apk.git \
  ~/.agents/skills/pull-android-apk
```

Claude Code 可放到 `~/.claude/skills/pull-android-apk`。其他工具使用其技能目录，保留整个文件夹，不能只复制 `SKILL.md`。具体发现路径以所用 Agent 版本的文档为准。

## 运行依赖

- Python 3.10 或更高版本，仅使用标准库。
- Android SDK Platform-Tools：`adb`。
- Android SDK Build-Tools：`aapt2`、`apksigner`。
- 可运行 `apksigner` 的 Java 环境，建议 JDK 17。
- 已开启 USB 调试、已授权当前电脑的设备或模拟器。

支持 Linux、macOS。Windows 使用 WSL，并先确认 WSL 中的 `adb devices` 能找到设备。Agent 必须能运行本地命令并访问 ADB；仅支持文件上传的聊天界面无法直接操作 USB 设备。

已安装 Android SDK Command-Line Tools 时，可按需安装依赖：

```bash
sdkmanager "platform-tools" "build-tools;36.0.0"
```

工具从 `PATH`、`ANDROID_HOME`、`ANDROID_SDK_ROOT` 或常见 SDK 目录发现，也可以通过命令参数指定路径。运行前检查：

```bash
python3 scripts/apk_pull.py doctor
```

## 使用

向 Agent 描述需求即可，例如：

> 将设备上 `com.example.app` 的主 APK 和所有拆分 APK 拉取到 `~/workspace/debug`。

也可以直接运行：

```bash
# 查看设备，并逐台检查指定包是否已安装
python3 scripts/apk_pull.py devices --package com.example.app

# 多台在线设备时必须指定 serial；输出目录必须尚不存在
python3 scripts/apk_pull.py pull \
  --serial DEVICE_SERIAL \
  --package com.example.app \
  --output ./exports/com.example.app

# 离线复核，不需要设备或 adb；仍需要 aapt2 和 apksigner
python3 scripts/apk_pull.py verify ./exports/com.example.app
```

输出示例：

```text
com.example.app/
  base.apk
  split_config.arm64_v8a.apk
  split_config.zh.apk
  SHA256SUMS
  manifest.json
  evidence/
```

实际 APK 名称和数量由设备的安装状态决定。输出目录不覆盖。文件在临时目录中拉取和校验，完成后发布到目标目录。

`manifest.json` 的字段、校验规则和完整性状态见[归档格式](references/export-format.md)。

## 完整性与失败处理

- 拉取 `pm path` 返回的每个 APK，并对照 `dumpsys package` 的拆分清单。
- 每个 APK 都验证签名；主包与拆分包必须具有相同包名、版本代码和签名证书。配置拆分包可以省略 `versionName`。
- 拉取前后对比 Package Manager 信息，应用更新、漏包和签名不一致都不能返回完整成功。
- 记录文件哈希、设备来源、工具版本及原始命令结果；`verify` 重新校验文件与记录的一致性。
- 失败的单次传输默认重试一次，可用 `--retries 0..3` 调整；`--pull-timeout` 默认每次 300 秒。
- 退出码：`0` 成功；`1` 保存了不完整归档；`2` 请求、环境或校验错误；`130` 用户中断。

部分失败时保留已经拉到的文件，并标记 `incomplete`。存在问题的归档不会被当作完整成功。

这里只导出当前设备**已经安装**的 APK。未安装的按需模块、OBB、应用私有数据不在范围内。脚本不会修改设备或应用，也不会联网下载应用。文件哈希和来源记录用于复核归档，不构成第三方签署的来源证明。

## 开发与维护

Skill、脚本、文档和测试均在本仓库维护。根目录的 `SKILL.md`、`agents/`、`scripts/`、`references/` 和 `LICENSE` 是维护源，`plugins/pull-android-apk/skills/pull-android-apk/` 保存用于原生插件安装的 Skill 副本。

修改源文件后，在仓库根目录生成分发副本并运行检查：

```bash
python3 scripts/build_plugin.py
python3 -S -m unittest discover -s tests -v
python3 scripts/build_plugin.py --check
```

测试使用模拟 ADB、AAPT2、APK Signer 和临时 APK，不连接真实设备，不需要 Android SDK。`-S` 禁用 Python 第三方包加载，用于检查运行时独立性。

CI 在 Linux 和 macOS 上运行测试，并检查分发副本与维护源一致。新增或删除分发文件时，同步修改 `scripts/build_plugin.py` 的文件清单，并清理分发目录中的旧文件。

Codex 和 Claude Code 分别使用 `.agents/plugins/marketplace.json` 与 `.claude-plugin/marketplace.json`，两者指向同一个插件目录。发布插件更新时，同步递增两份插件 manifest 和 Claude Code marketplace 条目中的版本号。

安装资料：[Agent Skills 规范](https://agentskills.io/specification)、[Skills CLI](https://github.com/vercel-labs/skills)、[Codex CLI 插件命令](https://developers.openai.com/codex/cli/reference#codex-plugin)、[Claude Code 插件安装](https://code.claude.com/docs/en/discover-plugins)。

## 许可证

[MIT](LICENSE)。仓库仅分发 Skill、脚本和测试，不包含设备导出的 APK 或来源记录。
