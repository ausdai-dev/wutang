# -*- coding: utf-8 -*-
"""
Patch frontend/_template.html to integrate:
1. Full-stack Auth API integration (POST /api/auth/login, POST /api/auth/register)
2. Default Admin / Admin quick autofill and hint
3. Registration two-step password mismatch real-time validation
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "frontend" / "_template.html"

def main():
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    print(f"Initial template length: {len(content)} chars")

    # 1. 更新登录表单提示与占位符
    OLD_LOGIN_ACCOUNT_INPUT = 'placeholder="输入账号或邮箱（主理人可输入 xush09@qq.com）"'
    NEW_LOGIN_ACCOUNT_INPUT = 'placeholder="输入常用邮箱 或 默认主理人: admin"'
    if OLD_LOGIN_ACCOUNT_INPUT in content:
        content = content.replace(OLD_LOGIN_ACCOUNT_INPUT, NEW_LOGIN_ACCOUNT_INPUT, 1)
        print("[ok] Updated login account placeholder")

    OLD_LOGIN_PWD_INPUT = 'placeholder="输入密码（主理人体验口令如 admin / 888）"'
    NEW_LOGIN_PWD_INPUT = 'placeholder="输入密码（默认主理人密码: admin）"'
    if OLD_LOGIN_PWD_INPUT in content:
        content = content.replace(OLD_LOGIN_PWD_INPUT, NEW_LOGIN_PWD_INPUT, 1)
        print("[ok] Updated login password placeholder")

    OLD_DEMO_BTN = '⚡ 一键演示体验（主理人 xush09 身份）'
    NEW_DEMO_BTN = '⚡ 一键填入默认主理人账号 (admin / admin)'
    if OLD_DEMO_BTN in content:
        content = content.replace(OLD_DEMO_BTN, NEW_DEMO_BTN, 1)
        print("[ok] Updated demo admin button text")

    # 2. 更新注册表单：增加两遍密码校验提示红字
    OLD_REG_CONFIRM = """        <input type="password" id="regInputConfirmPassword" class="form-input" placeholder="再次输入密码" style="width:100%;box-sizing:border-box;font-size:13px;padding:8px 12px;">

      </div>"""
    NEW_REG_CONFIRM = """        <input type="password" id="regInputConfirmPassword" class="form-input" placeholder="再次输入密码 (两遍校验)" style="width:100%;box-sizing:border-box;font-size:13px;padding:8px 12px;">
        <div id="regMismatchTip" style="display:none;color:#C0392B;font-size:11.5px;margin-top:3px;font-weight:500;">⚠️ 两次输入的密码不一致，请仔细核对</div>
      </div>"""
    if OLD_REG_CONFIRM in content:
        content = content.replace(OLD_REG_CONFIRM, NEW_REG_CONFIRM, 1)
        print("[ok] Added password mismatch tip in register form")

    # 3. 更新 authManager 与 registerUser 函数为真实 API 驱动
    OLD_AUTH_FUNCS = """  function authManager(passcodeOrEmail, password) {

    var val = (passcodeOrEmail || '').trim().toLowerCase();

    var pwd = (password || '').trim().toLowerCase();

    var isManagerAccount = (

      val === 'xush09@qq.com' ||

      val === 'admin' ||

      val.indexOf('xush09') !== -1 ||

      val === 'wutang888' ||

      val === 'demo' ||

      val === 'xiaoping' ||

      val === '主理人' ||

      pwd === 'admin' ||

      pwd === 'wutang888'

    );



    if (isManagerAccount) {

      appState.isManagerLoggedIn = true;

      appState.currentUser = null;

      localStorage.setItem('wutang_manager_active', 'true');

      localStorage.removeItem('wutang_current_user');

      updateManagerUI();

      if ($('modalAuth')) $('modalAuth').classList.remove('active');

      showToast('主理人身份已认证！顶栏已自动解锁「主理人工作台」👑');

    } else if (val) {

      // 普通注册用户登录

      appState.isManagerLoggedIn = false;

      appState.currentUser = {

        name: val.split('@')[0],

        account: val,

        role: 'user'

      };

      localStorage.removeItem('wutang_manager_active');

      localStorage.setItem('wutang_current_user', JSON.stringify(appState.currentUser));

      updateManagerUI();

      if ($('modalAuth')) $('modalAuth').classList.remove('active');

      showToast('登录成功，欢迎回来：' + appState.currentUser.name);

    } else {

      showToast('请输入账号或邮箱');

    }

  }



  function registerUser(nickname, account, pwd, confirmPwd) {

    var nick = (nickname || '').trim();

    var acc = (account || '').trim();

    var p = (pwd || '').trim();

    var cp = (confirmPwd || '').trim();



    if (!acc) {

      showToast('请输入常用邮箱或登录账号');

      return;

    }

    if (!p || p.length < 6) {

      showToast('设置密码请至少输入 6 位字符');

      return;

    }

    if (p !== cp) {

      showToast('两次输入的密码不一致，请重新核对');

      return;

    }"""

    NEW_AUTH_FUNCS = """  function authManager(passcodeOrEmail, password) {
    var val = (passcodeOrEmail || '').trim();
    var pwd = (password || '').trim();

    if (!val || !pwd) {
      showToast('请输入账号与密码');
      return;
    }

    // 调用后台标准认证接口
    fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account: val, password: pwd })
    }).then(function(res) {
      if (!res.ok) {
        return res.json().then(function(d) { throw new Error(d.detail || '账号或密码错误'); });
      }
      return res.json();
    }).then(function(data) {
      var user = data.user || {};
      appState.currentUser = user;
      appState.userNickname = user.daohao_nickname || user.username || '同修';
      if ($('userNicknameInput')) $('userNicknameInput').value = appState.userNickname;

      localStorage.setItem('wutang_auth_token', data.access_token);
      localStorage.setItem('wutang_current_user', JSON.stringify(user));

      if (user.role === 'admin') {
        appState.isManagerLoggedIn = true;
        localStorage.setItem('wutang_manager_active', 'true');
        showToast('主理人身份已认证！顶栏已自动解锁「主理人工作台」👑');
      } else {
        appState.isManagerLoggedIn = false;
        localStorage.removeItem('wutang_manager_active');
        showToast('登录成功，欢迎归堂：' + (user.daohao_nickname || user.username));
      }

      updateManagerUI();
      if ($('modalAuth')) $('modalAuth').classList.remove('active');
    }).catch(function(err) {
      // 离线兼容逻辑
      if (val === 'admin' && pwd === 'admin') {
        appState.isManagerLoggedIn = true;
        appState.userNickname = '悟堂主理人';
        localStorage.setItem('wutang_manager_active', 'true');
        updateManagerUI();
        if ($('modalAuth')) $('modalAuth').classList.remove('active');
        showToast('主理人身份已认证 (本地兼容态)！👑');
      } else {
        showToast(err.message || '登录失败，请检查账号密码');
      }
    });
  }

  function registerUser(nickname, account, pwd, confirmPwd) {
    var nick = (nickname || '').trim();
    var acc = (account || '').trim();
    var p = (pwd || '').trim();
    var cp = (confirmPwd || '').trim();

    if (!acc) {
      showToast('请输入常用注册邮箱');
      return;
    }
    if (!acc.match(/^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$/)) {
      showToast('请输入格式合法的电子邮箱地址');
      return;
    }
    if (!p || p.length < 6) {
      showToast('设置密码请至少输入 6 位字符');
      return;
    }
    if (p !== cp) {
      showToast('两次输入的密码不一致，请重新核对');
      if ($('regMismatchTip')) $('regMismatchTip').style.display = 'block';
      return;
    }

    fetch('http://localhost:8000/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: acc,
        password: p,
        confirm_password: cp,
        daohao_nickname: nick || null
      })
    }).then(function(res) {
      if (!res.ok) {
        return res.json().then(function(d) { throw new Error(d.detail || '注册失败'); });
      }
      return res.json();
    }).then(function(data) {
      var user = data.user || {};
      appState.currentUser = user;
      appState.userNickname = user.daohao_nickname || '同修';
      if ($('userNicknameInput')) $('userNicknameInput').value = appState.userNickname;

      localStorage.setItem('wutang_auth_token', data.access_token);
      localStorage.setItem('wutang_current_user', JSON.stringify(user));
      localStorage.removeItem('wutang_manager_active');
      appState.isManagerLoggedIn = false;

      updateManagerUI();
      if ($('modalAuth')) $('modalAuth').classList.remove('active');
      showToast('注册成功！欢迎步入悟堂修道人生。');
    }).catch(function(err) {
      showToast(err.message || '注册失败，请稍后重试');
    });
  }"""

    if OLD_AUTH_FUNCS in content:
        content = content.replace(OLD_AUTH_FUNCS, NEW_AUTH_FUNCS, 1)
        print("[ok] Replaced authManager and registerUser with real API calls")

    # 4. 更新快速演示按钮监听：一键填入 admin / admin
    OLD_DEMO_CLICK = """        if ($('authInputAccount')) $('authInputAccount').value = 'xush09@qq.com';

        if ($('authInputPassword')) $('authInputPassword').value = 'admin';

        authManager('xush09@qq.com', 'admin');"""
    NEW_DEMO_CLICK = """        if ($('authInputAccount')) $('authInputAccount').value = 'admin';
        if ($('authInputPassword')) $('authInputPassword').value = 'admin';
        authManager('admin', 'admin');"""
    if OLD_DEMO_CLICK in content:
        content = content.replace(OLD_DEMO_CLICK, NEW_DEMO_CLICK, 1)
        print("[ok] Updated demo click handler to admin/admin")

    # 5. 绑定实时密码不一致提示事件
    MISMATCH_EVENT = """
    if ($('regInputConfirmPassword') && $('regInputPassword')) {
      var checkMismatch = function() {
        var p = $('regInputPassword').value;
        var cp = $('regInputConfirmPassword').value;
        var tip = $('regMismatchTip');
        if (tip) {
          if (cp && p !== cp) {
            tip.style.display = 'block';
          } else {
            tip.style.display = 'none';
          }
        }
      };
      $('regInputConfirmPassword').oninput = checkMismatch;
      $('regInputPassword').oninput = checkMismatch;
    }
"""
    if "checkMismatch" not in content and "$('regInputConfirmPassword').onkeydown" in content:
        content = content.replace(
            "if ($('regInputConfirmPassword')) {",
            MISMATCH_EVENT + "\n    if ($('regInputConfirmPassword')) {",
            1
        )
        print("[ok] Injected real-time password mismatch detector")

    TEMPLATE_PATH.write_text(content, encoding="utf-8")
    print(f"[success] Updated {TEMPLATE_PATH}! Size: {len(content)} chars")

if __name__ == "__main__":
    main()
