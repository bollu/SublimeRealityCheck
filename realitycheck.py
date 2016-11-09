import sublime
import traceback

import sublime_plugin
import cgi
import copy

# https://github.com/commercialhaskell/intero/blob/master/elisp/intero.el#L1148


class LanguageEvaluator:
    def can_run_on_syntax(syntax):
        raise NotImplementedError("can_run_on_syntax() not implemented")

    def lineinfo(self, line, evaldata):
        raise NotImplementedError("eval() not implemented in subclass"
                                  "of LanguageEvaluator")


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

    def clear_context(self):
        self.globalvals = {}
        self.expr_to_eval_map = {}

    def eval_line(self, line):

        print("line: %s | globals: %s" % (line, self.globalvals))
        try:
            # update globals and locals
            exec(line, self.globalvals)

            # assuming it's an expression, evaluate it and save it
            if not "=" in line:
                print("|%s| does not have =" % line)
                DUMMY_LHS_NAME = "dummy_lhs"

                globals_copy = copy.copy(self.globalvals)
                exec("%s = %s" % (DUMMY_LHS_NAME, line), globals_copy)
                self.expr_to_eval_map[line] = globals_copy[DUMMY_LHS_NAME]
        except Exception as e:
            return


    def get_line_display_str(self, line):

        # try an eval
        evalval = self.expr_to_eval_map[line] if line in self.expr_to_eval_map else None
        content = ""

        if evalval:
            content += "<li><pre>"
            core_content = "%s :: %s" % (evalval, type(evalval).__name__)
            core_content = cgi.escape(core_content)
            content += core_content
            content += "</li></pre>"
            return content
        # exec had succeeded
        else:
            evaldata = {varname: varval
                        for varname, varval in self.globalvals.items()
                        if varname in line}

            # line has no valid variables
            if not evaldata:
                return None

            content = "<ul style='max-width: 300px; word-wrap:break-word'>"
            for k in evaldata:
                core_content = "%s: %s :: %s" % \
                                (k, evaldata[k], type(evaldata[k]))
                core_content = cgi.escape(core_content)

                content += "<li> <pre> %s </pre> </li>\n" % core_content
            content += "</ul>"

        return content

def does_content_exist(content, phantoms):
    for ps in phantoms:
        if ps.content == content:
            return True
    return False

class InterspyCommand(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.view = view
        self._phantoms = []

        self.pset = sublime.PhantomSet(self.view)
        self.evals = [PythonEvaluator()]
        self.should_update = True
        self.stall_update = False

        print("initing.")
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
        valid_evals = list(filter(lambda e: e.can_run_on_syntax(syntax),
                                  self.evals))

        # unable to find anything in the list, so return
        if not valid_evals:
            return None

        return valid_evals[0]

    def on_modified_async(self):
        print("modified: setting an update")
        self.stall_update = True
        self.should_update = True

        def reset_update():
            if self.stall_update:
                self.stall_update = False

        # do not allow ourselves to update for some ms
        sublime.set_timeout_async(reset_update, 20)

    def run_process(self):

        if not self.should_update:
            sublime.set_timeout_async(self.run_process, 10)
            return
        else:
            if self.stall_update:
                sublime.set_timeout_async(self.run_process, 10)
            else:
                sublime.set_timeout_async(self.run_process, 10)

            self.should_update = False

        if not self.evaluator:
            return

        # evaluate the entire file and cache the eval data
        # evaldata = self.evaluator.process_file(self.filestr)
        # reset all phantoms

        # find all regions to add hints
        hint_regions = self.view.lines(self.fileregion)

        self.evaluator.clear_context()

        for r in hint_regions:
            line_region = self.view.line(r.b)
            linestr = self.view.substr(line_region)

            self.evaluator.eval_line(linestr)
            contentstr = self.evaluator.get_line_display_str(linestr) 

            # evaluator failed. return None
            if contentstr is None:
                continue

            p = sublime.Phantom(line_region, contentstr, sublime.LAYOUT_BELOW)

            # if there is another phantom with
            # the same contentstr as us, don't add`
            if does_content_exist(contentstr, self.phantoms):
                continue
            else:
                # remove all old blocks with the same region
                self.phantoms = \
                        list(filter(lambda p:
                                    not p.region.intersects(line_region),
                                    self.phantoms))

                self.phantoms.append(DataRegion(contentstr, p, line_region))

        self.update_phantom_set()
