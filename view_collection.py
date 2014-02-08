import tempfile
import time
import sublime


class ViewCollection:
    views = {} # Todo: these aren't really views but handlers. Refactor/Rename.
    git_times = {}
    git_files = {}
    buf_files = {}
    pendings  = {}
    compare_against = "HEAD"

    @staticmethod
    def add(view):
        key = ViewCollection.get_key(view)
        try:
            from GitGutter.git_gutter_handler import GitGutterHandler
        except ImportError:
            from git_gutter_handler import GitGutterHandler
        handler = ViewCollection.views[key] = GitGutterHandler(view)
        handler.reset()
        return handler

    @staticmethod
    def debounce_add(view):
        def check(view):    
            key = ViewCollection.get_key(view)
            lines = len(view.lines(sublime.Region(0,view.size())))
            if key in ViewCollection.pendings:
                pend = ViewCollection.pendings[key]
                if time.time() - pend["time"] > 0.1 or lines != pend["lines"]:
                    del ViewCollection.pendings[key]
                    ViewCollection.add(view)
                else:
                    sublime.set_timeout(lambda: check(view), 50)

        key = ViewCollection.get_key(view)
        if key in ViewCollection.pendings:
            pend = ViewCollection.pendings[key]
            pend["time"] = time.time()
        else:
            lines = len(view.lines(sublime.Region(0,view.size())))
            ViewCollection.pendings[key] = {"time": time.time(), "lines": lines}
            sublime.set_timeout(lambda: check(view), 50)
            ViewCollection.add(view)

    @staticmethod
    def git_path(view):
        key = ViewCollection.get_key(view)
        if key in ViewCollection.views:
            return ViewCollection.views[key].get_git_path()
        else:
            return False

    @staticmethod
    def get_key(view):
        return view.file_name()

    @staticmethod
    def has_view(view):
        key = ViewCollection.get_key(view)
        return key in ViewCollection.views

    @staticmethod
    def get_handler(view):
        if ViewCollection.has_view(view):
            key = ViewCollection.get_key(view)
            return ViewCollection.views[key]
        else:
            return ViewCollection.add(view)

    @staticmethod
    def diff(view):
        key = ViewCollection.get_key(view)
        return ViewCollection.views[key].diff()

    @staticmethod
    def untracked(view):
        key = ViewCollection.get_key(view)
        return ViewCollection.views[key].untracked()

    @staticmethod
    def ignored(view):
        key = ViewCollection.get_key(view)
        return ViewCollection.views[key].ignored()

    @staticmethod
    def total_lines(view):
        key = ViewCollection.get_key(view)
        return ViewCollection.views[key].total_lines()

    @staticmethod
    def git_time(view):
        key = ViewCollection.get_key(view)
        if not key in ViewCollection.git_times:
            ViewCollection.git_times[key] = 0
        return time.time() - ViewCollection.git_times[key]

    @staticmethod
    def clear_git_time(view):
        key = ViewCollection.get_key(view)
        ViewCollection.git_times[key] = 0

    @staticmethod
    def update_git_time(view):
        key = ViewCollection.get_key(view)
        ViewCollection.git_times[key] = time.time()

    @staticmethod
    def git_tmp_file(view):
        key = ViewCollection.get_key(view)
        if not key in ViewCollection.git_files:
            ViewCollection.git_files[key] = tempfile.NamedTemporaryFile()
            ViewCollection.git_files[key].close()
        return ViewCollection.git_files[key]

    @staticmethod
    def buf_tmp_file(view):
        key = ViewCollection.get_key(view)
        if not key in ViewCollection.buf_files:
            ViewCollection.buf_files[key] = tempfile.NamedTemporaryFile()
            ViewCollection.buf_files[key].close()
        return ViewCollection.buf_files[key]

    @staticmethod
    def set_compare(commit):
        print("GitGutter now comparing against:",commit)
        ViewCollection.compare_against = commit

    @staticmethod
    def get_compare():
        if ViewCollection.compare_against:
            return ViewCollection.compare_against
        else:
            return "HEAD"
