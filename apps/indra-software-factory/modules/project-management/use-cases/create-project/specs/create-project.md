# Create a project

**Status:** Draft
**Audience:** The people who start a project; whoever builds the skill `create-project` of the plugin `project-management`

**Scope:** The use case that creates the three repositories of a new project

A use case of the module `project-management`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `create-project` of the plugin `project-management`; the actor of every requirement that names no other. |
| Project | The three repositories `<project>-specs`, `<project>-norms` and `<project>-code`, which `/project-management:create-project` creates together. |

## Create a project

```gherkin
Feature: Create a project
  In order to start each layer in its own repository, with the app enabled
  As a person who starts a project
  I want its three repositories created in one go

  Rule: ORC-1 The creation starts only when the user asks for it

    Scenario: The user types the command
      When the user types "/project-management:create-project"
      Then the creation of a project starts

    Scenario: The user asks in words
      When the user says they want to start a new project with its three repositories
      Then the creation of a project starts

    Scenario: The user only talks about projects
      When the user asks how a project is organized
      Then no creation starts

  Rule: ORC-2 The skill asks in one message for everything it was not given

    Scenario: Nothing given
      When the creation starts with no project name
      Then the skill asks, in one numbered message, for:
        | Question      | Default                            |
        | Project name  | none                               |
        | GitHub owner  | the account logged in to GitHub    |
        | Visibility    | private                            |
        | Local folder  | the current directory              |

    Scenario: The name given with the command
      When the user types "/project-management:create-project billing"
      Then the skill does not ask for the project name
      And it asks for the owner, the visibility and the local folder

    Scenario: A name that is not lowercase-dash
      When the user gives the project name "Billing App"
      Then the skill asks again for the name, in lowercase-dash

  Rule: ORC-3 Nothing is created when a check fails

    Scenario: The user is not logged in to GitHub
      Given the user is not logged in to GitHub
      When the creation of "billing" starts
      Then the skill creates nothing
      And it says that the user must log in to GitHub

    Scenario: A repository already exists
      Given the repository "billing-norms" exists on GitHub
      When the user gives the project name "billing"
      Then the skill creates nothing
      And it says that "billing-norms" already exists

    Scenario: A local folder already exists
      Given the folder "billing-code" exists in the local folder
      When the user gives the project name "billing"
      Then the skill creates nothing
      And it says that the folder "billing-code" already exists

  Rule: ORC-4 Nothing is created before the user approves the plan

    Scenario: The user approves
      Given every check passed for the project "billing"
      When the skill shows the plan
      And the user approves it
      Then the three repositories are created

    Scenario: The user does not approve
      Given every check passed for the project "billing"
      When the skill shows the plan
      And the user does not approve it
      Then the skill creates nothing

  Rule: ORC-5 Each repository starts with the app enabled

    Scenario Outline: The repository of one layer
      Given the user approved the plan for the project "billing"
      When the project is created
      Then the repository "billing-<layer>" exists on GitHub with the chosen owner and visibility
      And it is cloned in the local folder, beside the other two
      And its ".claude/settings.json" enables the plugin "indra-software-factory"
      And it holds a "CLAUDE.md" and a "README.md", pushed in its first commit

      Examples:
        | layer |
        | specs |
        | norms |
        | code  |

  Rule: ORC-19 A creation that fails halfway removes nothing and reports what exists

    Scenario: GitHub refuses the third repository
      Given the user approved the plan for the project "billing"
      And the repositories "billing-specs" and "billing-norms" were created
      When GitHub refuses to create "billing-code"
      Then the skill removes nothing
      And it stops
      And it reports which repositories and local folders exist, and the error that GitHub gave

  Rule: ORC-6 The skill reports where the project is and how to open it

    Scenario: The project was created
      Given the project "billing" was created
      Then the skill shows the URLs of the three repositories
      And it says to open each repository alone, in its own editor window
```
