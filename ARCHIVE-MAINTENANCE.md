# Morning Archive 归档管理

本项目的正式报告目录是 `reports/catalog.json`，独立网页位于 `reports/YYYY/MM/YYYY-MM-DD-{global|semiconductor|premarket}.html`。旧版 `reports/index.json` 不在当前自动清理范围内。

## 自动清理

GitHub Actions 工作流 `.github/workflows/report-maintenance.yml` 每月 1 日 09:15（Asia/Singapore，UTC 01:15）自动执行一次：

- global 全球新闻早报：30 天
- semiconductor 半导体晨报：90 天
- premarket 半导体盘前预警：14 天
- `reports/protected.json` 内的 ID 永不自动清理

只处理当前 `catalog.json` 中格式验证通过、具有实体 HTML 的条目，删除对应 HTML 后同步更新 catalog。清理结果保存在 `reports/cleanup-log.json`，Git 提交历史亦可用于恢复。

## 手动删除和收藏保护

1. 打开 Morning Archive 首页，点击「归档管理」，勾选报告并复制 ID。
2. 打开 [GitHub Actions · Morning Archive maintenance](https://github.com/wongtszshan/Morning-Archive-Web/actions/workflows/report-maintenance.yml)，点击 **Run workflow**。
3. **mode** 选 `delete`（删除）、`protect`（保护）、`unprotect`（取消保护），或 `cleanup`（按保留期限扫描）。
4. 在 **report_ids** 中粘贴逗号分隔 ID，例如 `2026-11-03-global,2026-11-03-semiconductor`。cleanup 不需要 ID。
5. 第一次保持 **apply** 未勾选，运行后在任务摘要中检查将要操作的对象。
6. 确认无误，重新运行并勾选 **apply** 才真正更改 GitHub 仓库。

已保护的报告不允许通过 delete 直接删除；必须先 unprotect。由于此网站是静态 GitHub Pages，网页不会存储 GitHub Token，也不会从匿名访客的浏览器直接删库。

## 保护逻辑和异常处理

- 目录中的 ID、类别、日期、文件路径必须一致；任意不一致或缺文件会使本次操作失败，不会误删未知路径。
- 手动删除只接受索引里存在的 ID。
- preview（apply 关闭）不改变任何文件。
- GitHub Actions 在变更前运行 `python -m unittest discover -s tests -v`。
- 每次提交删除时更新索引和 HTML；网站刷新即可获取新的目录。可能仍有 GitHub Pages CDN 缓存延迟。
- `reports/index.json` 是遗留正文数据，不自动删除。现有自动化或外部程序若写入 `catalog.json`，应在每次上传时保留未变更条目，并避免覆盖 `protected.json`。
