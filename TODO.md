# TODO

- [x] talk needs to take a input prompt, generates a response, summarizes the conversation
  - [x] talk: implement logger to log in json format capturing prompt, response, summary, and datetime stamp
  - [x] talk: implement these log messages to be stored in context.dat using writeback for performance
- [x] review works with two modes
  - [x] review: mode that retrieves the response when passed a prompt
  - [x] review: mode that retrieves the summary when passed a prompt
- [x] both review and talk work when context.dat doesn't exist
  - [x] talk: creates a proper context.dat
  - [x] review: creates a context.dat and alerts the user that no history exists yet.
- [x] Clean up code
  - [x] Delete make_history
  - [x] Refactor resummarize to take in a single prompt
- [x] Implement functionality to add new profiles
- [x] Implement input giving an input into talk
  - [x] Add functionality that takes in an input file
  - [x] Add functionality that takes in a dictionary