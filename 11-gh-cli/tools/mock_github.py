"""Small stand-in for github.com so gh and git can run for real without touching GitHub.
Serves https on 127.0.0.1:443 for github.com and api.github.com (tools/demo.sh points them here).
Only the requests the deck needs: device login, user, repos, issues, PRs, git over smart HTTP.
Usage: python3 mock_github.py REPO_DIR CERT_DIR"""
import http.server, json, os, subprocess, sys, re, shutil, gzip
ROOT = sys.argv[1]  # bare repos live in ROOT/kim/name.git
CERTS = sys.argv[2]  # chain.crt and srv.key from tools/demo.sh
import datetime
NOW = (datetime.datetime.utcnow() - datetime.timedelta(minutes=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
STATE = {"scopes": "gist, read:org, repo, workflow"}


def log(*a):
    sys.stderr.write(" ".join(str(x) for x in a) + "\n")
    sys.stderr.flush()


def repo_obj(owner, name, private=False):
    return {"id": "R_" + name, "name": name, "owner": {"login": owner, "id": "U_1"}, "nameWithOwner": f"{owner}/{name}",
            "description": "", "url": f"https://github.com/{owner}/{name}", "isPrivate": private,
            "visibility": "PRIVATE" if private else "PUBLIC",
            "viewerPermission": "ADMIN", "defaultBranchRef": {"name": "main"}, "parent": None, "isFork": False,
            "isArchived": False, "hasIssuesEnabled": True, "hasWikiEnabled": True, "pushedAt": NOW,
            "updatedAt": NOW, "createdAt": NOW,
            "stargazerCount": 0, "forkCount": 0, "watchers": {"totalCount": 0}, "issues": {"totalCount": 0},
            "pullRequests": {"totalCount": 0}, "sshUrl": f"git@github.com:{owner}/{name}.git",
            "mergeCommitAllowed": True, "rebaseMergeAllowed": True, "squashMergeAllowed": True,
            "isInOrganization": False, "isTemplate": False, "isEmpty": False, "viewerCanAdminister": True,
            "homepageUrl": "", "primaryLanguage": None, "repositoryTopics": {"nodes": []}, "licenseInfo": None}


ISSUES, PRS, CNT = [], [], {}
FIELDS = {"PullRequest": ["id", "number", "title", "state", "body", "author", "isDraft", "mergeable", "mergeStateStatus", "headRefOid", "projectItems", "autoMergeRequest", "reviewDecision"],
          "StatusCheckRollupContextConnection": ["checkRunCount", "checkRunCountsByState", "statusContextCount", "statusContextCountsByState"], "WorkflowRun": ["event", "workflow"]}


def NOW2():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def next_num(repo):
    CNT[repo] = CNT.get(repo, 0) + 1    # issues and PRs share numbers, like GitHub
    return CNT[repo]


def head_oid(repo, br):
    return subprocess.run(["git", "--git-dir", os.path.join(ROOT, "kim", repo + ".git"), "rev-parse", br], capture_output=True, text=True).stdout.strip()


def pr_obj(n, inp):
    repo = inp["repositoryId"][2:]
    return {"repo": repo, "id": f"PR_{n}", "number": n, "title": inp["title"], "body": inp.get("body", ""), "state": "OPEN", "url": f"https://github.com/kim/{repo}/pull/{n}",
            "author": {"login": "kim", "id": "U_1", "name": "kim"}, "autoMergeRequest": None, "isDraft": False, "maintainerCanModify": True,
            "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "additions": 1, "deletions": 0, "commits": {"totalCount": 1, "nodes": [{"commit": {"oid": head_oid(repo, inp["headRefName"])}}]},
            "baseRefName": inp["baseRefName"], "headRefName": inp["headRefName"], "headRefOid": head_oid(repo, inp["headRefName"]),
            "headRepositoryOwner": {"id": "U_1", "login": "kim", "name": "kim"}, "headRepository": {"id": "R_" + repo, "name": repo, "nameWithOwner": "kim/" + repo},
            "isCrossRepository": False, "reviewRequests": {"nodes": []}, "reviews": {"nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}, "totalCount": 0},
            "assignees": {"nodes": [], "totalCount": 0}, "labels": {"nodes": [], "totalCount": 0}, "milestone": None,
            "comments": {"nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}, "totalCount": 0}, "reactionGroups": [],
            "createdAt": NOW2(), "statusCheckRollup": {"nodes": [{"commit": {"statusCheckRollup": None}}]}, "projectCards": {"nodes": [], "totalCount": 0}}


def do_merge(p):
    import tempfile
    d = tempfile.mkdtemp()
    g = os.path.join(ROOT, "kim", p["repo"] + ".git")
    env = dict(os.environ, GIT_AUTHOR_NAME="kim", GIT_AUTHOR_EMAIL="kim@example.com", GIT_COMMITTER_NAME="GitHub", GIT_COMMITTER_EMAIL="noreply@github.com")
    subprocess.run(f"git clone -q {g} {d}/w && cd {d}/w && git merge -q --no-ff origin/{p['headRefName']} -m 'Merge pull request #{p['number']} from kim/{p['headRefName']}' -m '{p['title']}' && git push -q origin main", shell=True, env=env)
    p["state"] = "MERGED"


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def send_json(self, code, obj, hdr=None):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-Oauth-Scopes", STATE["scopes"])
        for k, v in (hdr or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def git(self, b):
        path, _, qs = self.path.partition("?")
        if self.headers.get("Content-Encoding") == "gzip":
            b = gzip.decompress(b)
        env = dict(os.environ, GIT_PROJECT_ROOT=ROOT, GIT_HTTP_EXPORT_ALL="1", PATH_INFO=path, QUERY_STRING=qs,
                   REQUEST_METHOD=self.command, CONTENT_TYPE=self.headers.get("Content-Type", ""),
                   REMOTE_USER="kim", REMOTE_ADDR="127.0.0.1", CONTENT_LENGTH=str(len(b)))
        out = subprocess.run(["git", "-c", "http.receivepack=true", "http-backend"], input=b, env=env, capture_output=True).stdout
        head, _, rest = out.partition(b"\r\n\r\n")
        status, hdrs = 200, []
        for line in head.decode().split("\r\n"):
            k, _, v = line.partition(": ")
            if k.lower() == "status":
                status = int(v.split()[0])
            elif k:
                hdrs.append((k, v))
        self.send_response(status)
        for k, v in hdrs:
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(rest)))
        self.end_headers()
        self.wfile.write(rest)

    def handle_any(self):
        b = self.body()
        host, path = self.headers.get("Host", ""), self.path
        log("REQ", self.command, host, path, b[:300])
        if "/info/refs" in path or "git-upload-pack" in path or "git-receive-pack" in path:
            return self.git(b)
        if path.startswith("/login/device/code"):
            STATE["asked"] = b.decode()
            return self.send_json(200, {"device_code": "dc1", "user_code": "8F2A-71C4",
                                        "verification_uri": "https://github.com/login/device", "expires_in": 899, "interval": 1})
        if path.startswith("/login/oauth/access_token"):
            if "delete_repo" in STATE.get("asked", ""):
                STATE["scopes"] = "delete_repo, gist, read:org, repo, workflow"
            return self.send_json(200, {"access_token": "gho_mocktoken", "token_type": "bearer", "scope": STATE["scopes"].replace(" ", "")})
        if path == "/" and host.startswith("api."):
            return self.send_json(200, {"current_user_url": "https://api.github.com/user"})
        m2 = re.match(r"^/repos/([^/]+)/([^/?]+)/readme", path)
        if m2:
            import base64
            d = os.path.join(ROOT, m2[1], m2[2] + ".git")
            txt = subprocess.run(["git", "--git-dir", d, "show", "main:README.md"], capture_output=True).stdout
            if not txt:
                return self.send_json(404, {"message": "Not Found"})
            return self.send_json(200, {"name": "README.md", "path": "README.md", "encoding": "base64", "content": base64.b64encode(txt).decode(),
                                        "html_url": f"https://github.com/{m2[1]}/{m2[2]}/blob/main/README.md"})
        if path.split("?")[0] in ("/user", "/api/v3/user"):
            return self.send_json(200, {"login": "kim", "id": 1, "name": "kim"})
        if path.startswith("/graphql"):
            q = json.loads(b or b"{}")
            text, var = q.get("query", ""), q.get("variables", {}) or {}
            log("GQL", " ".join(text.split())[:200], json.dumps(var)[:300])
            open(os.path.join(CERTS, "gql.log"), "a").write(" ".join(text.split()) + "\n" + json.dumps(var, ensure_ascii=False) + "\n\n")
            return self.send_json(200, self.gql(text, var))
        m = re.match(r"^/repos/([^/]+)/([^/?]+)$", path)
        if m and self.command == "DELETE":
            if "delete_repo" not in STATE["scopes"]:
                return self.send_json(403, {"message": "Must have admin rights to Repository.",
                                            "documentation_url": "https://docs.github.com/rest/repos/repos#delete-a-repository", "status": "403"})
            shutil.rmtree(os.path.join(ROOT, m[1], m[2] + ".git"), ignore_errors=True)
            self.send_response(204)
            self.send_header("X-Oauth-Scopes", STATE["scopes"])
            self.end_headers()
            return
        if m and self.command == "GET":
            return self.send_json(200, {"name": m[2], "full_name": f"{m[1]}/{m[2]}", "owner": {"login": m[1]},
                                        "html_url": f"https://github.com/{m[1]}/{m[2]}", "default_branch": "main", "private": False})
        return self.send_json(404, {"message": "Not Found"})

    def gql(self, text, var):
        own, name = var.get("owner", "kim"), var.get("name") or var.get("repo", "")
        u = f"https://github.com/{own}/{name}"
        if "__type(" in text:
            names = re.findall(r'(\w+): __type\(name: "(\w+)"\)', text)
            return {"data": {a: {"fields": [{"name": f} for f in FIELDS.get(t, [])]} for a, t in names}}
        if "createIssue" in text:
            inp = var["input"]; n = next_num(inp["repositoryId"][2:])
            ISSUES.append({"repo": inp["repositoryId"][2:], "number": n, "title": inp["title"], "body": inp.get("body", ""), "state": "OPEN", "url": f"https://github.com/kim/{inp['repositoryId'][2:]}/issues/{n}", "updatedAt": NOW2(), "labels": {"nodes": [], "totalCount": 0}, "stateReason": None})
            return {"data": {"createIssue": {"issue": {"id": f"I_{n}", "url": ISSUES[-1]["url"]}}}}
        if "query IssueList" in text:
            return {"data": {"repository": {"hasIssuesEnabled": True, "issues": {"totalCount": len([i for i in ISSUES if i["repo"] == name]), "nodes": [i for i in ISSUES if i["repo"] == name][::-1], "pageInfo": {"hasNextPage": False, "endCursor": None}}}}}
        if "createPullRequest" in text:
            inp = var["input"]; n = next_num(inp["repositoryId"][2:])
            PRS.append(pr_obj(n, inp))
            return {"data": {"createPullRequest": {"pullRequest": {"id": f"PR_{n}", "url": PRS[-1]["url"]}}}}
        if "query PullRequestForBranch" in text:
            nodes = [p for p in PRS if p["repo"] == name and p["headRefName"] == var["headRefName"] and p["state"] in var.get("states", ["OPEN"])]
            return {"data": {"repository": {"pullRequests": {"nodes": nodes}, "defaultBranchRef": {"name": "main"}}}}
        if "query PullRequestList" in text:
            st = var.get("state") or ["OPEN"]
            nodes = [p for p in PRS if p["repo"] == name and p["state"] in st][::-1]
            return {"data": {"repository": {"pullRequests": {"totalCount": len(nodes), "nodes": nodes, "pageInfo": {"hasNextPage": False, "endCursor": None}}}}}
        if "projectItems(" in text:
            return {"data": {"repository": {"pullRequest": {"projectItems": {"totalCount": 0, "nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}}}}}}
        if "pullRequest(number" in text:
            n = var.get("pr_number")
            for p in PRS:
                if p["repo"] == name and p["number"] == n:
                    return {"data": {"repository": {"pullRequest": p}}}
            return {"data": {"repository": {"pullRequest": None}}, "errors": [{"type": "NOT_FOUND", "message": f"Could not resolve to a PullRequest with the number of {n}."}]}
        if "mergePullRequest" in text:
            pid = var["input"]["pullRequestId"]
            for p in PRS:
                if p["id"] == pid:
                    do_merge(p)
            return {"data": {"mergePullRequest": {"clientMutationId": None}}}
        if "createRepository" in text:
            inp = var.get("input", {})
            nm = inp.get("name")
            subprocess.run(["git", "init", "-q", "--bare", "-b", "main", os.path.join(ROOT, "kim", nm + ".git")])
            return {"data": {"createRepository": {"repository": repo_obj("kim", nm, inp.get("visibility") == "PRIVATE")}}}
        if "repositories(" in text:
            nodes = [repo_obj("kim", d[:-4]) for d in sorted(os.listdir(os.path.join(ROOT, "kim")))]
            conn = {"totalCount": len(nodes), "nodes": nodes, "pageInfo": {"hasNextPage": False, "endCursor": None}}
            return {"data": {"viewer": {"login": "kim"}, "owner": {"login": "kim", "repositories": conn}, "repositoryOwner": {"login": "kim", "repositories": conn}}}
        al = re.findall(r'(repo_\d+): repository\(owner: "([^"]+)", name: "([^"]+)"\)', text)
        if al:
            d = {"viewer": {"login": "kim"}}
            for a, o, n in al:
                d[a] = repo_obj(o, n)
            return {"data": d}
        if "repository(" in text:
            if name and not os.path.isdir(os.path.join(ROOT, own, name + ".git")):
                return {"data": {"repository": None}, "errors": [{"type": "NOT_FOUND", "path": ["repository"], "message": f"Could not resolve to a Repository with the name '{own}/{name}'."}]}
            return {"data": {"repository": repo_obj(own, name)}}
        if "viewer" in text:
            return {"data": {"viewer": {"login": "kim"}}}
        return {"data": {}}

    do_GET = do_POST = do_DELETE = do_PATCH = do_PUT = handle_any


import ssl
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 443), H)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(os.path.join(CERTS, "chain.crt"), os.path.join(CERTS, "srv.key"))
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
srv.serve_forever()
