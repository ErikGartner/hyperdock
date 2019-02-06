# Contribution Guidelines
Adopted: *2019-02-05*

## Pull Requests

Pull requests are welcomed but please inform the core contributors of your intention through the issue tracker. Please note that all **pull request should be made to *dev***. Continue reading for more information on how to format commits.

## Committing
When committing there exists a set of guidelines and best practices.

A commit should:
  - only change one thing, i.e. fix one bug or add one feature
  - have attached test cases
  - have a correctly formatted commit message

### Branching Strategy

Hyperdock follows a light weight version of *git flow* like branching strategy combined with a *fix-forward* strategy.

This means that *master* is a dedicated release branch. Never directly commit to *master*. New commits are made to *dev* or a *feature* branch.

In general smaller fixes, documentation changes and features are added directly to *dev*. Larger, multi-commit, changes are made on *feature* branches. These are merged into *dev* when completed (with `git merge --no-ff`) and the feature branch is discarded.

List of branches:

  - *master* is a stable release branch
  - *dev* is the development branch
  - *feature/xyz* - feature branch containing a series of related commits

Fixes are never backported, instead all fixes are only applied forward as described above.

###  Message Format

Since these guidelines were adapted a Hyperdock commit should follow the below template.

```
[type]: [short description] #[Github issue number]

[
  Multiline Detailed explanation
]
```

Types are:
 - *feat* - the commit adds a feature
 - *fix* - the commit fixes a bug
 - *doc* - the commit updates the documentation
 - *build* - the commit adds to the build process
 - *rel* - the commit introduces a new release

### Dependencies

The Python dependencies are defined in `Pipfile`, `Pipfile.lock`, `requirements.txt` and `setup.py`. These must be identical and synced. The main authority is the `Pipfile` (a Pipenv versioning file), changes should first be made there, then synced to the other files.

The web interface has its dependencies defined in `web/.meteor/packages`, `web/.meteor/versions` ,`web/.meteor/release`,  `web/package.json` and `web/package-lock.json`. NPM packages are preferred over Meteor packages.

## Releasing

Releases are performed by tagging the HEAD of *master*. Note therefore that the HEAD of *master* should always be the latest release.

The release process:
  1. update the version number in `hyperdock/version.py`
  2. commit the updated version number
  3. create a git tag
  4. build and push the package to PyPI
  5. build and push the Docker images to DockerHub

### Versioning

Hyperdock adheres to [Semantic Versioning v2.0.0](https://semver.org/spec/v2.0.0.html).
