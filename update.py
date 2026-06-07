# -*- coding: utf-8 -*-
"""
agent-edu-reviewkit 一键更新脚本
用法：在项目目录下运行 python update.py
功能：将本地项目同步到 GitHub 仓库 main 分支的最新版本
"""

import subprocess
import sys
import os
import io


def setup_encoding():
    """解决 Windows 终端 GBK 编码无法显示 emoji 的问题"""
    if sys.platform == "win32":
        # 尝试设置控制台为 UTF-8
        try:
            os.system("chcp 65001 >nul 2>&1")
        except Exception:
            pass
        # 重新配置 stdout 为 UTF-8
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
        except Exception:
            pass


def run_git(*args):
    """运行 git 命令，返回 (成功, stdout, stderr)"""
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True, text=True, encoding="utf-8"
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()


def main():
    setup_encoding()

    # 1. 环境检查：是否为 git 仓库
    if not os.path.isdir(".git"):
        print("❌ 当前目录不是 git 仓库")
        print("   请先运行: git clone https://github.com/lijiawei255/agent-edu-reviewkit.git")
        sys.exit(1)

    # 检查远程 origin 是否存在
    ok, out, _ = run_git("remote", "get-url", "origin")
    if not ok:
        print("❌ 未找到远程仓库 origin")
        sys.exit(1)
    print(f"📡 远程仓库: {out}")

    # 检查当前分支
    ok, branch, _ = run_git("branch", "--show-current")
    if not ok:
        print("❌ 无法获取当前分支")
        sys.exit(1)

    if branch != "main":
        print(f"⚠️  当前分支为 '{branch}'，不是 main 分支")
        ans = input("   是否切换到 main 分支再更新？(y/N): ").strip().lower()
        if ans == "y":
            ok, _, err = run_git("checkout", "main")
            if not ok:
                print(f"❌ 切换分支失败: {err}")
                sys.exit(1)
            branch = "main"
            print("   ✅ 已切换到 main 分支")
        else:
            print("   取消更新")
            sys.exit(0)

    # 检查是否有未提交的修改
    ok, status, _ = run_git("status", "--porcelain")
    if ok and status:
        print("⚠️  检测到本地未提交的修改：")
        for line in status.split("\n")[:10]:
            print(f"   {line}")
        if status.count("\n") > 9:
            print(f"   ... 共 {len(status.split(chr(10)))} 个文件")
        print()
        print("   请选择处理方式：")
        print("   [1] git stash 暂存修改 → 更新 → 恢复修改（推荐）")
        print("   [2] 放弃本地修改，直接更新")
        print("   [3] 取消更新")
        ans = input("   请输入选项 (1/2/3): ").strip()
        if ans == "1":
            print("   📦 正在暂存本地修改...")
            ok_stash, _, err_stash = run_git("stash", "push", "-m", "update.py 自动暂存（更新前）")
            if not ok_stash:
                print(f"   ❌ 暂存失败: {err_stash}")
                sys.exit(1)
            print("   ✅ 本地修改已暂存")
            _stashed = True
        elif ans == "2":
            print("   🗑️  正在放弃本地修改...")
            ok_co, _, err_co = run_git("checkout", ".")
            if not ok_co:
                print(f"   ❌ 放弃修改失败: {err_co}")
                sys.exit(1)
            # 同时清理未跟踪的文件
            run_git("clean", "-fd")
            print("   ✅ 本地修改已放弃")
            _stashed = False
        else:
            print("   更新已取消")
            sys.exit(0)
    else:
        _stashed = False

    # 2. 获取远程最新状态
    print("🔍 正在检查更新...")
    ok, _, err = run_git("fetch", "origin", "main")
    if not ok:
        print(f"❌ 网络请求失败: {err}")
        print("   请检查网络连接后重试")
        sys.exit(1)

    # 3. 比较差异
    ok, local_hash, _ = run_git("rev-parse", "HEAD")
    ok2, remote_hash, _ = run_git("rev-parse", "origin/main")
    if not ok or not ok2:
        print("❌ 无法获取版本信息")
        sys.exit(1)

    if local_hash == remote_hash:
        print(f"✅ 已是最新版本 ({local_hash[:7]})，无需更新")
        sys.exit(0)

    # 检查是否可 fast-forward
    ok, merge_base, _ = run_git("merge-base", "HEAD", "origin/main")
    if ok and merge_base != local_hash:
        print("⚠️  本地 main 分支与远程 main 分支存在分歧（非 fast-forward）")
        print("   建议手动解决: git pull --rebase origin main")
        print("   或使用 git reset --hard origin/main 强制同步（会丢失本地提交）")
        sys.exit(1)

    # 展示更新内容
    ok, log, _ = run_git("log", "--oneline", f"{local_hash}..{remote_hash}")
    if ok and log:
        commits = log.split("\n")
        print(f"📦 发现 {len(commits)} 个新提交：")
        for c in commits[:10]:
            print(f"   {c}")
        if len(commits) > 10:
            print(f"   ... 还有 {len(commits) - 10} 个提交")
    else:
        print("📦 发现更新内容")

    # 4. 执行更新
    print("⬇️  正在更新...")
    ok, out, err = run_git("pull", "--ff-only", "origin", "main")
    if not ok:
        print(f"❌ 更新失败: {err}")
        sys.exit(1)

    # 5. 结果展示
    ok, new_hash, _ = run_git("rev-parse", "HEAD")
    if ok:
        print(f"✅ 更新成功！{local_hash[:7]} → {new_hash[:7]}")
    else:
        print("✅ 更新成功！")

    # 恢复暂存的本地修改
    if _stashed:
        print("📦 正在恢复本地修改...")
        ok_pop, _, err_pop = run_git("stash", "pop")
        if ok_pop:
            print("   ✅ 本地修改已恢复")
        else:
            print(f"   ⚠️  恢复修改时出现冲突: {err_pop}")
            print("   你的修改保存在 git stash 中，请手动处理: git stash pop")

    # 确认课程资料和输出文件夹不受影响
    print()
    if os.path.isdir("课程资料") or os.path.isdir("复习文档输出"):
        print("🔒 `课程资料/` 和 `复习文档输出/` 中的内容完好无损，不受更新影响。")

    # 检查关键文件变更
    ok, diff, _ = run_git("diff", f"{local_hash}..{new_hash if ok else remote_hash}", "--name-only")
    if ok and diff:
        changed = diff.split("\n")
        # 检查依赖
        if "requirements.txt" in changed:
            print("📋 requirements.txt 已更新，建议运行: pip install -r requirements.txt")
        # 检查 Python 脚本
        py_changed = [f for f in changed if f.endswith('.py') and f not in ('requirements.txt',)]
        if py_changed:
            print("🐍 以下 Python 脚本已更新:")
            for f in py_changed:
                print(f"   - {f}")
        # 检查技能文件
        skill_changed = [f for f in changed if f.startswith('skills/')]
        if skill_changed:
            print("📝 以下技能文件已更新:")
            for f in skill_changed:
                print(f"   - {f}")
        # 检查文档
        doc_changed = [f for f in changed if f.endswith('.md') and f not in ('skills/',)]
        if doc_changed:
            print("📖 以下文档已更新:")
            for f in doc_changed:
                print(f"   - {f}")


if __name__ == "__main__":
    main()
