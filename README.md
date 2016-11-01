InterpSpy
=========
** About

proof-of-concept plugin for immediate feedback with Python code


** Installation
<!-- this is copy-pasted from sublimeCodeIntel. Thanks for the great description! -->

**With the Package Control plugin:** The easiest way to install `InterpSpy` is through Package Control, which can be found at this site: http://wbond.net/sublime_packages/package_control

Once you install Package Control, restart Sublime Text and bring up the Command Palette (``Command+Shift+P`` on OS X, ``Control+Shift+P`` on Linux/Windows). Select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select `InterpSpy` when the list appears. The advantage of using this method is that Package Control will automatically keep `InterpSpy` up to date with the latest version.



**Without Git:** Download the latest source from `GitHub <https://github.com/bollu/InterpSpy/tree/re>` and copy the whole directory into the Packages directory.

**With Git:** Clone the repository in your Sublime Text Packages directory, located somewhere in user's "Home" directory ::
    git clone https://github.com/bollu/SublimeInterpSpy.git

** Development

Help me add more features! The first thing to do is to add support
for more languages. Implement more `LanguageExtension` instances and
send me a pull request!

**** NOTE: For a new release to be pushed, it needs to be tagged!


** Future Goals

- integrate with [Jupyter](http://jupyter.org/)?
- Add support for matplotlib to render diagrams
- Write an extensible API that can be hooked into other languages
- Add support for rich media (images, gifs, etc)
- Add more languages (I will add Haskell soon)
- Plan on adding C++ through Cling


