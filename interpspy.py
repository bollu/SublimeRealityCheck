import sublime

import sublime_plugin
import cgi

# https://github.com/commercialhaskell/intero/blob/master/elisp/intero.el#L1148


class LanguageEvaluator:
    def can_run_on_syntax(syntax):
        raise NotImplementedError("can_run_on_syntax() not implemented")

    def lineinfo(self, line, evaldata):
        raise NotImplementedError("eval() not implemented in subclass"
                                  "of LanguageEvaluator")


# TODO: use this to replace the (r, p)
class DataRegion:
    def __init__(self, content, phantom, region):
        assert isinstance(content, str)
        assert isinstance(phantom, sublime.Phantom)
        assert isinstance(region, sublime.Region)

        self._content = content
        self._region = region
        self._phantom = phantom

    @property
    def content(self):
        return self._content

    @property
    def region(self):
        return self._region

    @property
    def phantom(self):
        return self._phantom


class PythonEvaluator(LanguageEvaluator):
    def can_run_on_syntax(self, syntax):
        return "python" in syntax.lower()

    def process_file(self, string):
        try:
            namespace = {}
            exec(string, globals(), namespace)
            return namespace
        except Exception as e:
            print("tried to exec. %s\nerror: %s" % (string, e))


    def _try_eval_line(self, line):
        try:
            evalval = eval(line)
            return evalval
        except Exception as e:
            print("tried to eval |%s|\nerror: %s" % (line, e))


    def lineinfo(self, line, evaldata):


        content = ""

        # try an eval
        evalval = self._try_eval_line(line)
        if evalval:
            content += "<li><pre>"
            core_content = "%s :: %s" % (evalval, type(evalval).__name__)
            core_content = cgi.escape(core_content)
            content += core_content
            content += "</li></pre>"
        # exec had succeeded
        elif evaldata:

            evaldata = {varname: varval
                        for varname, varval in evaldata.items()
                        if varname in line}

            # line has no valid variables
            if not evaldata:
                return None

            content = "<ul style='max-width: 300px; word-wrap:break-word'>"
            for k in evaldata:
                core_content = "%s :: %s" % (k, evaldata[k])
                core_content = cgi.escape(core_content)

                content += "<li> <pre> %s </pre> </li>\n" % core_content
            content += "</ul>"

        return content


class InterspyCommand(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.view = view
        self._phantoms = []

        self.pset = sublime.PhantomSet(self.view)
        self.evals = [PythonEvaluator()]
        self.should_update = True
        self.stall_update = False

        sublime.set_timeout_async(self.run_process, 500)

    def update_phantom_set(self):
        ps = [d.phantom for d in self._phantoms]
        self.pset.update(ps)


    @property
    def phantoms(self):
        return self._phantoms

    @phantoms.setter
    def phantoms(self, value):
        assert isinstance(value, list)
        self._phantoms = value

        self.update_phantom_set()

    @property
    def fileregion(self):
        return sublime.Region(0, self.view.size() + 1)

    @property
    def filestr(self):
        return self.view.substr(self.fileregion)

    @property
    def evaluator(self):
        syntax = self.view.settings().get('syntax')
        valid_evals = filter(lambda e: e.can_run_on_syntax(syntax),
                             self.evals)

        # unable to find anything in the list, so return
        if not valid_evals:
            return None

        return list(valid_evals)[0]

    def on_modified_async(self):
        print("modified: setting an update")
        self.stall_update = True
        self.should_update = True

        def reset_update():
            self.stall_update = False

        # do not allow ourselves to update for the next 200ms
        sublime.set_timeout_async(reset_update, 80)

    def run_process(self):
        sublime.set_timeout_async(self.run_process, 500)


        if (not self.should_update) or self.stall_update:
            return
        else:
            self.should_update = False

        cursor = self.view.sel()[0]
        cursor_line_region = self.view.line(cursor)

        if not self.evaluator:
            return

        # evaluate the entire file and cache the eval data
        evaldata = self.evaluator.process_file(self.filestr)
        # reset all phantoms
        # self.phantoms = []


        # find all regions to add hints
        # hint_regions = self.view.find_all('=')
        # cursor is not being hinted, add it
        # if not any(cursor.intersects(r) for r in hint_regions):
        # hint_regions.append(cursor_line_region)
        hint_regions = self.view.lines(self.fileregion)

        for r in hint_regions:
            line_region = self.view.line(r.b)
            linestr = self.view.substr(line_region)
            content = None


            # remove old phantoms that were on the same line

            content = self.evaluator.lineinfo(linestr, evaldata)
            
            # evaluator failed. return None
            if content is None:
                continue

            p = sublime.Phantom(line_region, content, sublime.LAYOUT_BELOW)

            # this is a new block, not an old block
            if not any(ph.content == content for ph in self.phantoms):
                self.phantoms = list(filter(lambda p: not p.region.intersects(line_region), self.phantoms))

                self.phantoms.append(DataRegion(content, p, line_region))

        self.update_phantom_set()



