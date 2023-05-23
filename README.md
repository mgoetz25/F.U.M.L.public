# F.U.M.L.
F.U.M.L. (F.U.M.L. Uses Machine Learning) proposes a machine-learning-driven solution to accelerate the process of entering forms into a database.

## Branch Structure
(Draft, feel free to modify). There are two branches that live forever: main and dev.

Let the commits on the main branch represent an almost production-ready state of the project.

Let the commits on the dev branch represent an implementation of a single feature.

Branches should be made off of the dev branch that represent individual features. When a feature branch is at an almost production-ready state, make a pull request ot merge the feature branch to the dev branch. You do not have to delete the feature branch if you intend to make a new, working version of the feature and later do another pull request.

When the state of the dev branch reaches a produciton-ready state, you can make a pull request to merge it into the main branch. At least one other person should look at, and varify, the changes of the pull request before merging dev to main.

## Directory Structure
```
/docs         (documentation)
/fuml         (core content: business logic, tests, utilities, webpages, etc.)
  /utils      (helper modules, tools, data, etc.)
  /templates  (webpages)
  /tests      (code tests)
```
