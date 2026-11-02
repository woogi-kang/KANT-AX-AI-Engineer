"""Runs every command of the deck as kim and prints what stays on screen (see tools/demo.sh)."""
import os, subprocess, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drive import run

R = os.environ["GH_DEMO_REPOS"]
K = "/home/kim"


def sh(c, cwd=K):
    subprocess.run(c, shell=True, cwd=cwd, check=True, env=dict(os.environ, HOME=K))


def show(cwd, cmd, steps=(), prompt=None):
    out, rc = run(cwd, cmd, steps)
    p = prompt or ("~" + cwd[len(K):] if cwd.startswith(K) else cwd)
    print(f"\n$ [{p}] {cmd}")
    print("\n".join(out))
    print(f"[rc={rc}]")


# fresh /home/kim and mock repos (also when practice.py imports this file)
if True:
    shutil.rmtree(K, ignore_errors=True)
    shutil.rmtree(R, ignore_errors=True)
    os.makedirs(K + "/kant")
    os.makedirs(R + "/kim")
    sh("git config --global user.name kim && git config --global user.email kim@example.com && git config --global init.defaultBranch main && git config --global pull.rebase false")
    sh(f"git init -q --bare -b main {R}/kim/team-intro.git")
    sh(f"git clone -q {R}/kim/team-intro.git {R}/../seed 2>/dev/null; cd {R}/../seed && printf '# team-intro\\n\\n우리 팀 소개 페이지예요.\\n' > README.md && git add README.md && git commit -q -m 'docs: README 추가' && echo '# kim' > kim.md && git add kim.md && git commit -q -m 'feat: kim 소개 추가' && git push -q origin main; rm -rf {R}/../seed")
    sh(f"git init -q --bare -b main {R}/kim/hello-git.git")

if __name__ == "__main__":
    print("== part 1")
    show(K, "gh --version")
    show(K, "gh auth status")
    print("== part 2 login")
    show(K, "gh auth login", [(b"Where do you use", "ENTER"), (b"preferred protocol", "ENTER"), (b"Authenticate Git", "Y+ENTER"),
                              (b"How would you like", "ENTER"), (b"Press Enter", "ENTER")])
    show(K, "gh auth status")
    show(K, "cat ~/.gitconfig")
    print("== part 3 clone")
    show(K + "/kant", "gh repo clone kim/team-intro")
    show(K + "/kant/team-intro", "git remote -v")
    show(K + "/kant/team-intro", "git log --oneline")
    show(K + "/kant/team-intro", "gh repo view")
    show(K + "/kant/team-intro", "gh browse")
    show(K, "gh repo list")
    print("== part 4 create")
    os.makedirs(K + "/kant/my-notes")
    show(K + "/kant/my-notes", "git init")
    show(K + "/kant/my-notes", "echo '# my-notes' > README.md && git add README.md && git commit -m 'docs: README 추가'")
    show(K + "/kant/my-notes", "gh repo create my-notes --public --source=. --remote=origin")
    show(K + "/kant/my-notes", "git remote -v")
    show(K + "/kant/my-notes", "git push origin main")
    show(K, "gh repo list")
    print("== part 5 delete")
    show(K, "gh repo delete kim/my-notes", [(b"to confirm deletion", "kim/my-notes+ENTER")])
    show(K, "gh auth refresh -h github.com -s delete_repo", [(b"Press Enter", "ENTER")])
    show(K, "gh auth status")
    show(K, "gh repo delete kim/my-notes", [(b"to confirm deletion", "kim/my-notes+ENTER")])
    show(K, "gh repo list")
    show(K + "/kant/my-notes", "git push origin main")
    print("== part 6 simple")
    T = K + "/kant/team-intro"
    show(T, 'gh issue create --title "소개 페이지에 사진 넣기" --body "각자 사진 한 장씩 넣어요"')
    show(T, "gh issue list")
    show(T, "git checkout -b feature/kim-hobby")
    show(T, "echo '취미: 등산' >> kim.md && git add kim.md && git commit -m 'feat: kim 취미 추가'")
    show(T, "git push origin feature/kim-hobby")
    show(T, 'gh pr create --title "feat: kim 취미 추가" --body "kim.md에 취미를 적었어요"')
    show(T, "gh pr list")
    show(T, "gh pr view 2")
    show(T, "gh pr merge 2 --merge")
    show(T, "git checkout main")
    show(T, "git pull origin main")
    show(T, "git log --oneline")
    print("== extra")
    show(K, "gh --help | head -40")
    show(K, "gh repo --help | head -30")
