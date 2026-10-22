# -*- coding: utf-8 -*-
"""
悟堂 · 注册、登录与修道身份认证全量验证套件 (Auth Suite)
验证目标：
1. 默认管理员账号 (admin / admin) 开机播种与登录鉴权
2. 注册：邮箱校验 + 密码两遍一致性硬门禁校验 (密码两遍校验)
3. 注册：密码最小长度校验与邮箱防重校验
4. JWT Token 标准签发与 GET /api/auth/me 受保护接口鉴权
5. 个人修道道号更新与权限隔离
"""
import sys
import time
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import app

results = []

def check(name: str, condition: bool, extra: str = ""):
    status = "✓" if condition else "✗"
    msg = f"  [{status}] {name}"
    if extra:
        msg += f" ({extra})"
    print(msg)
    results.append({"name": name, "pass": bool(condition)})

def run_auth_checks():
    client = TestClient(app)
    print("\n=================================================================")
    print("🔐 悟堂 · 用户系统、注册登录与主理人权限全量验收套件")
    print("=================================================================\n")

    # 1. 默认主理人账号 (admin / admin) 登录
    print("--- 1. 默认主理人管理员账号 (admin / admin) 鉴权 ---")
    admin_login_resp = client.post("/api/auth/login", json={
        "account": "admin",
        "password": "admin"
    })
    check("默认管理员 admin / admin 登录成功", admin_login_resp.status_code == 200)
    admin_data = admin_login_resp.json()
    admin_token = admin_data.get("access_token", "")
    admin_user = admin_data.get("user", {})
    check("管理员身份角色为 admin", admin_user.get("role") == "admin")
    check("管理员道号为「悟堂主理人」", admin_user.get("daohao_nickname") == "悟堂主理人")
    check("颁发有效 JWT 令牌", bool(admin_token) and len(admin_token.split(".")) == 3)

    # 2. 错误密码拦截
    wrong_login = client.post("/api/auth/login", json={
        "account": "admin",
        "password": "wrongpassword"
    })
    check("错误密码被安全拦截 (400)", wrong_login.status_code == 400)

    # 3. 注册流程与两遍密码校验
    print("\n--- 2. 注册功能：邮箱与两遍密码一致性强校验 ---")
    # 测试两遍密码不一致
    mismatch_resp = client.post("/api/auth/register", json={
        "email": "test_mismatch@wutang.com",
        "password": "password123",
        "confirm_password": "password456",
        "daohao_nickname": "求道者"
    })
    check("两次密码不一致时被严格拦截 (400)", mismatch_resp.status_code == 400 and "两次输入的密码不一致" in mismatch_resp.json().get("detail", ""))

    # 测试非法邮箱格式
    invalid_email_resp = client.post("/api/auth/register", json={
        "email": "invalid_email_format",
        "password": "password123",
        "confirm_password": "password123"
    })
    check("非法邮箱格式被拦截 (400)", invalid_email_resp.status_code == 400)

    # 测试密码过短 (< 6 位)
    short_pwd_resp = client.post("/api/auth/register", json={
        "email": "short@wutang.com",
        "password": "123",
        "confirm_password": "123"
    })
    check("短密码 (<6位) 被拦截 (400/422)", short_pwd_resp.status_code in [400, 422])

    # 测试正常注册成功
    test_email = f"wutang_user_{int(time.time())}@example.com"
    reg_resp = client.post("/api/auth/register", json={
        "email": test_email,
        "password": "securePassword2026",
        "confirm_password": "securePassword2026",
        "daohao_nickname": "归真子"
    })
    check("合法邮箱+两次相同密码注册成功 (200)", reg_resp.status_code == 200)
    reg_data = reg_resp.json()
    new_token = reg_data.get("access_token")
    new_user = reg_data.get("user", {})
    check("新注册用户道号生效", new_user.get("daohao_nickname") == "归真子")
    check("新注册用户角色为普通修道者 (user)", new_user.get("role") == "user")

    # 测试重复邮箱注册被拦截
    dup_resp = client.post("/api/auth/register", json={
        "email": test_email,
        "password": "securePassword2026",
        "confirm_password": "securePassword2026"
    })
    check("重复邮箱注册被拦截 (400)", dup_resp.status_code == 400 and "该邮箱已被注册" in dup_resp.json().get("detail", ""))

    # 4. 新用户登录
    print("\n--- 3. 新注册用户登录与 Token 鉴权 ---")
    user_login_resp = client.post("/api/auth/login", json={
        "account": test_email,
        "password": "securePassword2026"
    })
    check("新用户使用邮箱登录成功 (200)", user_login_resp.status_code == 200)

    # 5. 受保护接口 GET /api/auth/me 校验
    print("\n--- 4. 受保护接口 GET /api/auth/me 与道号更新 ---")
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_token}"})
    check("GET /api/auth/me 凭有效 Token 访问成功 (200)", me_resp.status_code == 200)
    me_user = me_resp.json().get("user", {})
    check("正确返回个人修道档案 (归真子)", me_user.get("daohao_nickname") == "归真子")

    # 无 Token 访问应被拦截
    no_token_resp = client.get("/api/auth/me")
    check("未提供 Token 访问被安全拦截 (401)", no_token_resp.status_code == 401)

    # 6. 更新修道道号
    profile_update_resp = client.put(
        "/api/auth/profile",
        json={"daohao_nickname": "清风同修", "preferred_track": "daoism"},
        headers={"Authorization": f"Bearer {new_token}"}
    )
    check("PUT /api/auth/profile 更新道号成功", profile_update_resp.status_code == 200)
    updated_user = profile_update_resp.json().get("user", {})
    check("道号成功变更为「清风同修」", updated_user.get("daohao_nickname") == "清风同修")
    check("偏好流派更新为道家 (daoism)", updated_user.get("preferred_track") == "daoism")

    # 汇总
    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    print("\n=================================================================")
    print(f"📊 Auth 验收结果: {passed}/{total} 项测试全部通过")
    if passed == total:
        print("🎉 悟堂 · 用户注册登录系统 (含 admin/admin 播种与密码双重校验) 已 100% 达标！")
    else:
        print("⚠️ 存在未通过项，请检查上方日志。")
    print("=================================================================\n")

if __name__ == "__main__":
    run_auth_checks()
