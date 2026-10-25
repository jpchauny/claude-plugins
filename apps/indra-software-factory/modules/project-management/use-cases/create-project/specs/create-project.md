# Create a project

**Audience:** The people who start a project; whoever builds the skill `create-project` of the plugin `project-management`

**Scope:** The use case that creates the repositories of the four layers of a new project, and its `project.json`

A use case of the module `project-management`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `create-project` of the plugin `project-management`; the actor of every requirement that names no other. |
| Project | The repositories of its four layers ([LAY-1](../../../../../specs/layers.md#lay-1--every-project-has-four-layers-each-in-its-own-repositories)), as its `project.json` lists them ([ORC-20](../../../specs/module.md#where-the-repositories-are)). |
| Project folder | The folder that holds the repositories of a project ([ORC-20](../../../specs/module.md#where-the-repositories-are)). |

## Create a project

```gherkin
Feature: Create a project
  In order to start each layer in its own repository, with the modules of its layer enabled
  As a person who starts a project
  I want the repositories of its four layers created in one go

  Rule: ORC-1 The creation starts only when the user asks for it

    Scenario: The user types the command
      When the user types "/project-management:create-project"
      Then the creation of a project starts

    Scenario: The user asks in words
      When the user says they want to start a new project with its repositories
      Then the creation of a project starts

    Scenario: The user only talks about projects
      When the user asks how a project is organized
      Then no creation starts

  Rule: ORC-2 The skill asks in one message for everything it was not given, and then for the names of the components

    Scenario: Nothing given
      When the creation starts with no project name
      Then the skill asks, in one numbered message, for:
        | Question            | Default                                       |
        | Project name        | none                                          |
        | More than one component | no: layer 3 is one repository           |
        | GitHub owner        | the account logged in to GitHub               |
        | Visibility          | private                                       |
        | Project folder      | the folder "<project>" in the current directory |

    Scenario: The name given with the command
      When the user types "/project-management:create-project billing"
      Then the skill does not ask for the project name
      And it asks whether there is more than one component, the owner, the visibility and the project folder

    Scenario: One component
      When the user answers that there is not more than one component
      Then the skill does not ask for the names of the components
      And layer 3 is one repository, "<project>-code"

    Scenario: More than one component
      When the user answers that there is more than one component
      Then the skill asks, in a second message, for the names of the components
      And layer 3 is one repository "<project>-code-<component>" per component

    Scenario: Fewer than two names
      Given the user answered that there is more than one component
      When the user gives only the component "api"
      Then the skill asks again for the names of the components, at least two

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

    Scenario: The project folder already exists
      Given the project folder "billing" exists
      When the user gives the project name "billing"
      Then the skill creates nothing
      And it says that the folder "billing" already exists

    Scenario: A component that is not lowercase-dash
      When the user gives the component "Web App"
      Then the skill asks again for the components, in lowercase-dash

  Rule: ORC-4 Nothing is created before the user approves the plan

    Scenario: The user approves
      Given every check passed for the project "billing"
      When the skill shows the plan
      And the user approves it
      Then the repositories of the plan are created

    Scenario: The user does not approve
      Given every check passed for the project "billing"
      When the skill shows the plan
      And the user does not approve it
      Then the skill creates nothing

  Rule: ORC-5 Each repository starts with the modules of its layer enabled, as APP-6 says, and with the project's project.json

    Scenario Outline: The repository of one layer
      Given the user approved the plan for the project "billing", with no component
      When the project is created
      Then the repository "<repository>" exists on GitHub with the chosen owner and visibility
      And it is cloned in the project folder, in the folder "<repository>"
      And its ".claude/settings.json" enables the plugins "utilities" and "<module>", and no other plugin
      And it holds a "CLAUDE.md", a "README.md" and the "project.json" of the project, pushed in its first commit

      Examples:
        | repository     | module              |
        | billing-drafts | specs-management    |
        | billing-specs  | specs-management    |
        | billing-norms  | norms-management    |
        | billing-code   | code-implementation |

    Scenario: A project with components
      Given the user approved the plan for the project "billing", with the components "api" and "web"
      When the project is created
      Then layer 3 is the repositories "billing-code-api" and "billing-code-web", and there is no "billing-code"
      And each of them is created as the repository of one layer

    Scenario Outline: The repositories that people write ask before every commit and push
      Given the user approved the plan for the project "billing"
      When the project is created
      Then the ".claude/settings.json" of "<repository>" holds the rules "ask" "Bash(git commit *)", "Bash(git push *)", "Bash(git * commit *)" and "Bash(git * push *)" (LAY-2)

      Examples:
        | repository     |
        | billing-drafts |
        | billing-specs  |

    Scenario: The project.json of the project
      Given the user approved the plan for the project "billing", with the owner "acme"
      When the project is created
      Then every repository holds the same "project.json", with one entry per repository, its "owner" "acme", its "name", its "layer", its "component" when it has one, and its "path" equal to its "name" (ORC-20)

  Rule: ORC-19 A creation that fails halfway removes nothing and reports what exists

    Scenario: GitHub refuses a repository
      Given the user approved the plan for the project "billing"
      And the repositories "billing-drafts", "billing-specs" and "billing-norms" were created
      When GitHub refuses to create "billing-code"
      Then the skill removes nothing
      And it stops
      And it reports which repositories and local folders exist, and the error that GitHub gave

  Rule: ORC-6 The skill reports where the project is and how to open it

    Scenario: The project was created
      Given the project "billing" was created
      Then the skill shows the URLs of every repository of the project
      And it says to open each repository alone, in its own editor window
```
