from typing import List, Union
import hashlib
import gzip
import brotli
import os
import re

IGNORED: List[str] = ["node_modules", "elm-stuff", "builds", "tests"]


def task_pip():
    return {
        "actions": [
            "pip-compile --output-file=requirements.txt requirements.in",
            "pip-sync",
            "sed -i -e '/macfsevents/d' requirements.txt",
        ],
        "file_dep": ["requirements.in", "dodo.py"],
        "targets": ["requirements.txt"],
    }


def create_index():
    hasher = hashlib.sha256()
    content = open(f"static/elm.js", "rb").read()
    hasher.update(content)
    hexdiget = "hashed-" + hasher.hexdigest()[:10]
    open(f"static/elm.%s.js" % hexdiget, "wb").write(content)
    gzip.open(f"static/elm.%s.js.gz" % hexdiget, "wb").write(content)
    open(f"static/elm.%s.js.br" % hexdiget, "wb").write(
        brotli.compress(content, mode=brotli.MODE_TEXT, quality=11, lgwin=22)
    )
    open("index.html", "w").write(
        open("index.template.html").read().replace("__hash__", hexdiget)
    )


def elm_with(folder: str, target: str = "static"):
    def spec():
        basename = folder if folder else "elm"
        prefix = folder + "/" if folder else ""
        static = target if target.endswith("/") else (target + "/")

        realm_deps: List[str] = glob2(
            "realm/frontend/", r".*\.(elm|js)", recursive=True
        ) + ["dodo.py"] + glob2("Common", r".*\.elm$", recursive=True)

        yield {
            "actions": [
                "find %s | grep elm | grep -v elm.js | xargs -r rm" % (static,),
                create_index,
            ],
            "file_dep": [
                "dodo.py",
                "%selm.js" % static,
                "%sindex.template.html" % (prefix,),
            ],
            "targets": ["%sindex.html" % (prefix,)],
            "basename": basename,
            "name": "index",
        }

        proj_elms: List[str] = glob2(
            "%sfrontend" % (prefix,), r".*\.elm", recursive=True
        ) + ["%sfrontend/elm.json" % (prefix,)]
        main_elms: List[str] = [
            e.replace("%sfrontend/" % (prefix,), "")
            for e in proj_elms
            if "Pages/" in e and "Test.elm" not in e
        ]
        test_elms: List[str] = [
            e.replace("%sfrontend/" % (prefix,), "") for e in proj_elms if "Pages/" in e
        ]

        yield {
            "actions": [
                "cd %sfrontend && elm make Test.elm --output=elm-stuff/t.js"
                % (prefix,),
                "cat %sfrontend/elm-stuff/t.js realm/frontend/IframeController.js "
                "   > %stest.js" % (prefix, static),
            ],
            "file_dep": proj_elms + realm_deps,
            "targets": ["%stest.js" % (static,)],
            "basename": basename,
            "name": "test",
        }

        yield {
            "actions": [
                "cd %sfrontend && elm make Storybook.elm  --output=elm-stuff/s.js"
                % (prefix,),
                "cat %sfrontend/elm-stuff/s.js realm/frontend/IframeController.js "
                "   > %sstorybook.js" % (prefix, static),
            ],
            "file_dep": proj_elms + realm_deps,
            "targets": ["%sstorybook.js" % (static,)],
            "basename": basename,
            "name": "storybook",
        }

        elm_cmd = " ".join(
            ["cd %sfrontend && elm" % (prefix,), "make", "--output=elm-stuff/i.js"]
            + test_elms
        )
        yield {
            "actions": [
                elm_cmd,
                "cat %sfrontend/elm-stuff/i.js realm/frontend/Realm.js "
                "   > %siframe.js" % (prefix, static),
            ],
            "file_dep": proj_elms + realm_deps,
            "targets": ["%siframe.js" % (static,)],
            "basename": basename,
            "name": "iframe",
        }

        elm_cmd = " ".join(
            ["cd %sfrontend && elm" % (prefix,), "make", "--output=elm-stuff/e.js"]
            + main_elms
        )

        yield {
            "actions": [
                elm_cmd,
                # uglify_cmd,
                # "echo >> elm-stuff/e.min.js",
                "cat %sfrontend/elm-stuff/e.js realm/frontend/Realm.js"
                "   > %selm.js" % (prefix, static),
            ],
            "file_dep": proj_elms + realm_deps,
            "targets": ["%selm.js" % (static,)],
            "basename": basename,
            "name": "main",
        }

    return spec


task_elm = elm_with("")


MAIN_ELM = re.compile(r"\Wmain\W")
TARGETS = ["elm", "iframe", "test", "storybook"]


def glob2(
    path: str,
    patterns: str,
    blacklist: Union[str, List[str]] = None,
    recursive: bool = False,
    links: bool = True,
) -> List[str]:
    if blacklist is None:
        blacklist = IGNORED

    ls = os.listdir(path)
    ls = [os.path.join(path, f1) for f1 in ls]

    if blacklist:
        if type(blacklist) is str:
            blacklist = [blacklist]
        ls = [e for e in ls if not any(re.search(p, e) for p in blacklist)]

    if type(patterns) is str:
        patterns = [patterns]

    files = [
        e
        for e in ls
        if os.path.isfile(e) and any(re.search(patt, e) for patt in patterns)
    ]

    if recursive:
        dirs = [e for e in ls if os.path.isdir(e) and (links or not os.path.islink(e))]
        for d in dirs:
            files.extend(glob2(d, patterns, blacklist, recursive, links))

    return files
