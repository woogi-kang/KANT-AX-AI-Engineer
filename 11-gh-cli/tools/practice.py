"""Runs the README practice (sections 1 to 5) in order as kim, to check that every line works."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import demo  # noqa: F401  (importing demo.py makes a fresh /home/kim and the mock repos)
from demo import show, K, R

LOGIN = [(b"Where do you use", "ENTER"), (b"preferred protocol", "ENTER"), (b"Authenticate Git", "Y+ENTER"), (b"How would you like", "ENTER"), (b"Press Enter", "ENTER")]
print("== 1")
show(K, "gh --version")
show(K, "gh auth status")
show(K, "gh auth login", LOGIN)
show(K, "gh auth status")
print("== 2")
show(K + "/kant", "gh repo clone kim/team-intro")
T = K + "/kant/team-intro"
for c in ("git remote -v", "gh repo view", "gh browse", "gh repo list"):
    show(T, c)
print("== 3")
os.makedirs(K + "/kant/my-notes")
M = K + "/kant/my-notes"
for c in ("git init", "echo '# my-notes' > README.md", "git add README.md", "git commit -m 'docs: README 추가'",
          "gh repo create my-notes --public --source=. --remote=origin", "git remote -v", "git push origin main", "gh repo list"):
    show(M, c)
print("== 4")
for c in ('gh issue create --title "할 일 적기" --body "README에 할 일을 적어요"', "gh issue list", "git checkout -b feature/todo",
          "echo '- gh 연습하기' >> README.md", "git add README.md", "git commit -m 'docs: 할 일 추가'", "git push origin feature/todo",
          'gh pr create --title "docs: 할 일 추가" --body "README에 할 일을 적었어요"', "gh pr list", "gh pr view 2", "gh pr merge 2 --merge",
          "git checkout main", "git pull origin main", "git log --oneline"):
    show(M, c)
print("== 5")
CONF = [(b"to confirm deletion", "kim/my-notes+ENTER")]
show(K + "/kant", "gh repo delete kim/my-notes", CONF)
show(K + "/kant", "gh auth refresh -h github.com -s delete_repo", [(b"Press Enter", "ENTER")])
show(K + "/kant", "gh auth status")
show(K + "/kant", "gh repo delete kim/my-notes", CONF)
show(K + "/kant", "gh repo list")
