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

    def eval(self, string):
        try:
            namespace = {}
            exec(string, globals(), namespace)
            return namespace
        except Exception as e:
            print("tried to exec. %s\nerror: %s" % (string, e))

        try:
            evalval = {"__eval__": eval(string)}
            return evalval
        except Exception as e:
            print("tried to eval %s\nerror: %s" % (string, e))

    def lineinfo(self, line, evaldata):
        assert evaldata is not None

        content = ""
        if "__eval__" in evaldata:
            print("__eval__ present")
            val = evaldata["__eval__"]
            content += "<li><pre>"
            core_content = "%s :: %s" % (val, type(val).__name__)
            core_content = cgi.escape(core_content)
            content += core_content
            content += "</li></pre>"

        else:

            evaldata = {varname: varval
                        for varname, varval in evaldata.items()
                        if varname in line}

            # line has no valid variables
            if not evaldata:
                return None

            content = "<ul>"
            for k in evaldata:
                core_content = "%s :: %s" % (k, evaldata[k])
                core_content = cgi.escape(core_content)

                content += "<li> <pre> %s </pre> </li>\n" % core_content
            content += "</ul>"

        return content

        # try:
        #     namespace = {}
        #     exec(string, globals(), namespace)
        #     namespace = {varname: varval 
        #                     for varname, varval in namespace.items()
        #                     if varname in line }

        #     if not namespace:
        #         raise RuntimeError("namespace e")

        #     content = "<ul>"
        #     for k in namespace:
        #         core_content = "%s :: %s" % (k, namespace[k])
        #         core_content = cgi.escape(core_content)
        #         content += "<li> <pre> %s </pre> </li>\n" % core_content
        #     content += "</ul>"
        #     return content
        # except Exception as e:
        #     print("tried to exec. error: %s" % e)

        # # try Eval, will work for most things
        # try:
        #     evalval = eval(string)
        #     content = "%s :: %s" % (evalval, type(evalval).__name__)
        #     return content
        # except Exception as e:
        #     print("tried to eval. error: %s" % e)




class InterspyCommand(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.view = view
        self._phantoms = []

        self.pset = sublime.PhantomSet(self.view)

        self.evals = [PythonEvaluator()]

    @property
    def phantoms(self):
        return self._phantoms

    @phantoms.setter
    def phantoms(self, value):
        assert isinstance(value, list)
        self._phantoms = value

        ps = [p for (r, p) in self._phantoms]
        self.pset.update(ps)


    @property
    def filestr(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

    @property
    def evaluator(self):
        syntax = self.view.settings().get('syntax')
        valid_evals = filter(lambda e: e.can_run_on_syntax(syntax),
                             self.evals)

        # unable to find anything in the list, so return
        if not valid_evals:
            return None

        return list(valid_evals)[0]

    def on_modified(self):
        cursor = self.view.sel()[0]
        cursor_region = self.view.line(cursor)

        if not self.evaluator:
            return

        # evaluate the entire file and cache the eval data
        evaldata = self.evaluator.eval(self.filestr)
        if not evaldata:
            return

        # reset all phantoms
        self.phantoms = []


        # find all assignments
        assignments = self.view.find_all('=')

        for r in assignments:
            line_region = self.view.line(r.b)
            linestr = self.view.substr(line_region)
            content = None

            print("linestr: %s" % (linestr))

            # remove old phantoms that were on the same line

            content = self.evaluator.lineinfo(linestr, evaldata)
            
            # evaluator failed. return None
            if content is None:
                continue

            print("content: %s" % content)
            p = sublime.Phantom(line_region, content, sublime.LAYOUT_BELOW)

            self.phantoms.append((line_region, p))
            
        ps = [p for (r, p) in self._phantoms]
        self.pset.update(ps)


