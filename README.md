RealityCheck
=========

## About

proof-of-concept plugin for immediate feedback with Python code

![Demo GIF](http://i.imgur.com/30DnAYu.gifv)


## Installation
<!-- this is copy-pasted from sublimeCodeIntel. Thanks for the great description! -->

**With the Package Control plugin:** The easiest way to install `RealityCheck` is through Package Control, which can be found at this site: http://wbond.net/sublime_packages/package_control

Once you install Package Control, restart Sublime Text and bring up the Command Palette (``Command+Shift+P`` on OS X, ``Control+Shift+P`` on Linux/Windows). Select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select `RealityCheck` when the list appears. The advantage of using this method is that Package Control will automatically keep `RealityCheck` up to date with the latest version.


**With Git:** Clone the repository in your Sublime Text Packages directory, located somewhere in user's "Home" directory ::
    git clone https://github.com/bollu/SublimeRealityCheck.git

## Development

Help me add more features! The first thing to do is to add support
for more languages. Implement more `LanguageExtension` instances and
send me a pull request.

#### NOTE: For a new release to be pushed, it needs to be tagged!


## Future Goals

- integrate with [Jupyter](http://jupyter.org/)?
- Add support for matplotlib to render diagrams
- Write an extensible API that can be hooked into other languages
- Add support for rich media (images, gifs, etc)
- Add more languages (I will add Haskell soon)
- Plan on adding C++ through Cling


