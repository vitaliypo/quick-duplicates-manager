# Warning: The project is in development status. Using it may cause data loss.

## Yes, this is another duplicate files manager

... but with group operations, quick actions assignment with hotkeys and support of hard links.  
No, it can't search for duplicates (yet?). :)

## Background
I was unhappy with the way duplicate managers usually handle the process of viewing duplicates list and assigning actions to them.
Most of them focus on the duplicates search but not on comfortable and intuitive actions assignment process. It is especially painful to assign actions to thousands of duplicate files.  
So I decided to try make my own "perfect" tool for that purpose.

## Key features implemented:
* Ability to parse CloneSpy duplicates list file to create a table representation of duplicates
* Actions assignment using hotkeys: "Delete" (D), "Hardlink" (H), "Source for Hardlink" (S) (because every hardlink needs a source, right?)
* Action assignment for all siblings of the file (files found in the same location) with one button click
* Rules validation and errors highlight with navigation (Previous/Next error)
* Actions execution (actual deletion of files to recycle bin and creation of hardlinks)
* Count of groups of duplicates which have no actions assigned yet (aka "how much more groups I have to check?")
* UI tests
* Loading CloneSpy duplicates list by user's choice
* Open location of selected file or location of all files in selected group (only proof of concept is already implemented - need to open actual location instead of hardcoded)

## Features I want to implement in the nearest future:
* Progress bar for files processing (need to put files processing into separate thread)
* Validation of possibility to create Hard links (e.g. files are on the same partition, on NTFS filesystem, etc...)
* Refactor current code, make better structuring of classes and methods
* More UI tests :)

## Features to implement even later:
* Duplicates search
* Undo/Redo action assignment
* Session management (save/load current actions assigned to duplicates etc)
* Validation if files loaded from report actually exist
* Linux/MacOS support
* ... and more

## All info below is just a draft, don't try to find anything useful there.

## Getting Started

todo

### Prerequisites

todo

```
Give examples
```

### Installing

todo

## Running the tests

todo

### Break down into end to end tests

todo
```
Give an example
```

### And coding style tests

todo
```
Give an example
```

## Deployment

todo

## Built With
todo
* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgements

* Hat tip to anyone whose code was used
* Inspiration
* etc
