
# CHANGELOG

- [0.1.0] 3:30 am Dec 27 2022
  - Made .contexts db into folder
  - Changed .gitignore to ignore all things in the .contexts folder
  - Refactored companion.py to have simpler interface to contexts
  - Used the similar refactor to make sure the logs directory is properly created and exists

## [Unreleased]

## [0.1.0] - Tue Dec 27 01:11:13 MST 2022
### Added
- talk: take a input prompt, generates a response, summarizes the conversation
- talk: logger to log in json format capturing prompt, response, summary, and datetime stamp
- talk: log messages stored in context.dat using writeback for performance
- review: mode that retrieves the response when passed a prompt
- review: mode that retrieves the summary when passed a prompt
- both review and talk work when context.dat doesn't exist
- talk: creates a proper context.dat
- review: creates a context.dat and alerts the user that no history exists yet.
- Clean up code
- Delete make_history
- Refactor resummarize to take in a single prompt
- Implement functionality to add new profiles
- Implement input giving an input into talk
- Add functionality that takes in an input file
- Add functionality that takes in a dictionary of input files

## [0.0.1] - Tue Dec 27 01:11:13 MST 2022
### Added
- Initial release