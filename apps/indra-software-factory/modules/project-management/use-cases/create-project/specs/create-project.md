# Create a project

**Prefix:** CRP

**Audience:** The people who start a project; whoever builds the skill `create-project` of the plugin `project-management`

**Scope:** The use case that creates the repositories of the five layers of a new project, its orchestration repository and its tooling repository, and its `project.json`. Out of scope: the files of the acceptance repository that this use case does not write, such as its acceptance areas, acceptance units, acceptance tests and records ([ACU-6](../../../../acceptance-management/specs/module.md#the-files-of-the-acceptance-repository))

A use case of the module `project-management`, specified in [module.md](../../../specs/module.md); the modules of the app are listed in [app.md](../../../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Skill | The skill `create-project` of the plugin `project-management`; the actor of every requirement that names no other. |
| Project | The repositories of its five layers ([LAY-1](../../../../development-methodology/specs/layers.md#rules)), its orchestration repository ([LAY-11](../../../../development-methodology/specs/layers.md#the-orchestration-repository)) and its tooling repository ([LAY-14](../../../../development-methodology/specs/layers.md#the-tooling-repository)), as its `project.json` lists them ([ORC-20](../../../specs/module.md#where-the-repositories-are)). |
| Project folder | The folder that holds the repositories of a project ([ORC-20](../../../specs/module.md#where-the-repositories-are)). |

## Create a project

```gherkin
Feature: Create a project
  In order to start each layer in its own repository, with the modules of its layer enabled
  As a person who starts a project
  I want the repositories of its five layers, its orchestration repository and its tooling repository created in one go

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
        | More than one component | no: layer 4 is one repository           |
        | GitHub owner        | the account logged in to GitHub               |
        | Visibility          | private                                       |
        | Project folder      | the folder "<project>" in the current directory |
        | Default done profile | none                                          |

    Scenario: The name given with the command
      When the user types "/project-management:create-project billing"
      Then the skill does not ask for the project name
      And it asks whether there is more than one component, the owner, the visibility, the project folder and the default done profile

    Scenario: One component
      When the user answers that there is not more than one component
      Then the skill does not ask for the names of the components
      And layer 4 is one repository, "<project>-code"

    Scenario: More than one component
      When the user answers that there is more than one component
      Then the skill asks, in a second message, for the names of the components
      And layer 4 is one repository "<project>-code-<component>" per component

    Scenario: Fewer than two names
      Given the user answered that there is more than one component
      When the user gives only the component "api"
      Then the skill asks again for the names of the components, at least two

    Scenario: A name that is not lowercase-dash
      When the user gives the project name "Billing App"
      Then the skill asks again for the name, in lowercase-dash

    Scenario: A default done profile that is not a done profile
      When the user gives the default done profile "beta"
      Then the skill asks again for it, one of "prototype", "product" or "critical" (ACU-19, ACU-20)

  Rule: ORC-3 Nothing is created when a check fails

    Scenario: The user is not logged in to GitHub
      Given the user is not logged in to GitHub
      When the creation of "billing" starts
      Then the skill creates nothing
      And it says that the user must log in to GitHub

    Scenario: The token of GitHub lacks the scope "workflow"
      Given the continuous integration of the acceptance repository is enabled (ACU-76), so that the skill writes a workflow (CRP-1)
      And the token of the user's login to GitHub does not have the scope "workflow"
      When the creation of "billing" starts
      Then the skill creates nothing
      And it says to run "gh auth refresh -s workflow"

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

  Rule: ORC-5 Each repository of a layer, and the orchestration repository, starts with the modules that APP-6 enables in it, with the rules "ask" and "deny" of its layer, and with the project's project.json

    Scenario Outline: One repository of the project
      Given the user approved the plan for the project "billing", with no component
      When the project is created
      Then the repository "<repository>" exists on GitHub with the chosen owner and visibility
      And it is cloned in the project folder, in the folder "<repository>"
      And its ".claude/settings.json" enables the plugins "development-methodology", "utilities" and "<module>", and no other plugin
      And it holds a "CLAUDE.md", a "README.md" and the "project.json" of the project, pushed in its first commit
      And its default branch is "main"

      Examples:
        | repository         | module                     |
        | billing-drafts     | specs-management           |
        | billing-specs      | specs-management           |
        | billing-norms      | norms-management           |
        | billing-acceptance | acceptance-management |
        | billing-code       | code-implementation        |
        | billing-orchestration | workflow-orchestration  |

    Scenario: A project with components
      Given the user approved the plan for the project "billing", with the components "api" and "web"
      When the project is created
      Then layer 4 is the repositories "billing-code-api" and "billing-code-web", and there is no "billing-code"
      And layer 3 is the one repository "billing-acceptance", for every component (LAY-1)
      And each of them is created as one repository of the project

    Scenario Outline: The repositories whose every change a person approves ask before every commit and push
      Given the user approved the plan for the project "billing"
      When the project is created
      Then the ".claude/settings.json" of "<repository>" holds the rules "ask" "Bash(git commit *)", "Bash(git push *)", "Bash(git * commit *)" and "Bash(git * push *)" (<clause>)

      Examples:
        | repository         | clause |
        | billing-drafts     | LAY-2  |
        | billing-specs      | LAY-2  |
        | billing-acceptance | LAY-9  |

    Scenario Outline: The repositories of layers 3 and 4 deny the paths of the other role
      Given the user approved the plan for the project "billing", with the components "api" and "web"
      When the project is created
      Then the ".claude/settings.json" of "<repository>" holds the rules "deny" <rules>, and no other rule "deny" (ACU-13, level 1)

      Examples:
        | repository         | rules                                                                                                                                            |
        | billing-acceptance | "Read(//**/billing-code-api/**)", "Edit(//**/billing-code-api/**)", "Read(//**/billing-code-web/**)" and "Edit(//**/billing-code-web/**)"        |
        | billing-code-api   | "Edit(//**/billing-acceptance/**)"                                                                                                               |
        | billing-code-web   | "Edit(//**/billing-acceptance/**)"                                                                                                               |

    Scenario: A rule "deny" names the folder of the other repository at any depth
      Given the user approved the plan for the project "billing"
      When the skill writes a rule "deny" for the repository whose "path" is "billing-code"
      Then the rule names the path "//**/billing-code/**": anchored at the root of the file system, the folder "billing-code" at any depth

    Scenario: The repositories of layers 0, 1 and 2, the orchestration repository and the tooling repository deny nothing
      Given the user approved the plan for the project "billing"
      When the project is created
      Then the ".claude/settings.json" of "billing-drafts", "billing-specs", "billing-norms", "billing-orchestration" and "billing-tooling" holds no rule "deny"

    Scenario: The project.json of the project
      Given the user approved the plan for the project "billing", with the owner "acme"
      When the project is created
      Then every repository holds the same "project.json", with one entry per repository, its "owner" "acme", its "name", its "layer", or the "role" "orchestration" for "billing-orchestration" and the "role" "tooling" for "billing-tooling", its "component" when it has one, and its "path" equal to its "name" (ORC-20)
      And the entries are in this order: the repositories of layers 0 to 4, in the order of their layers and of their components, then "billing-orchestration", then "billing-tooling"
      And "project.json" has no "derived_norms": the project has no type of derived norms until a person adds one (NRM-1)

  Rule: CRP-4 The tooling repository starts as an empty marketplace of Claude Code, developed with the meta methodology, and with the module "utilities" alone
    Rationale: the tooling repository holds the project's own plugins (LAY-14), so it starts as a marketplace that lists none, ready for the first; it runs none of the methodology, which its plugins help to apply, so that the app never develops its own tools; "utilities" is for any project (APP-6).

    Scenario: The tooling repository
      Given the user approved the plan for the project "billing", with the owner "acme"
      When the project is created
      Then the repository "billing-tooling" exists on GitHub with the chosen owner and visibility
      And it is cloned in the project folder, in the folder "billing-tooling"
      And its ".claude/settings.json" enables the plugin "utilities", and no other plugin, and holds no rule "ask" and no rule "deny"
      And it holds a "CLAUDE.md", a "README.md", the "project.json" of the project and ".claude-plugin/marketplace.json", pushed in its first commit
      And its default branch is "main"

    Scenario: The marketplace of the tooling repository
      Given the user approved the plan for the project "billing", with the owner "acme"
      When the project is created
      Then ".claude-plugin/marketplace.json" of "billing-tooling" is the JSON object below, with the fields in this order, written with an indent of two spaces and ended by one line feed:
        """
        {
          "name": "billing-tooling",
          "owner": {
            "name": "acme"
          },
          "plugins": []
        }
        """

    Scenario: The CLAUDE.md of the tooling repository
      Given the user approved the plan for the project "billing", with the owner "acme"
      When the project is created
      Then the "CLAUDE.md" of "billing-tooling" says that the repository is the tooling repository of "billing" and no layer (LAY-14)
      And it says that every change starts in a spec that the person approves, and is implemented from it, by the meta methodology, citing "development.md" by its URL (LAY-14)
      And it says that a repository of a layer installs a plugin of it with "extraKnownMarketplaces" and "enabledPlugins", as LAY-14 says

    Scenario: No layer installs the tooling repository when the project is created
      Given the user approved the plan for the project "billing"
      When the project is created
      Then no ".claude/settings.json" of the project names the marketplace "billing-tooling", since it has no plugin yet (LAY-14)

  Rule: CRP-1 Once the continuous integration of the acceptance repository is enabled (ACU-76), the skill writes its workflow, and no workflow in a repository of layer 4

    Scenario: The workflow of the acceptance repository and its events
      Given the continuous integration of the acceptance repository is enabled (ACU-76)
      And the user approved the plan for the project "billing", with the owner "acme" and the components "api" and "web"
      When the project is created
      Then "billing-acceptance" holds ".github/workflows/acceptance.yml", which runs on a schedule, every hour at minute 17 UTC, and on a push to "main" that changes a file outside "records/" (ACU-34)
      And it runs on no other event

    Scenario: The script that the workflow of the acceptance repository runs
      Given the project "billing" was created
      When the workflow ".github/workflows/acceptance.yml" of "billing-acceptance" runs
      Then it runs the script "acceptance_ci.py" of the plugin "acceptance-management" from the branch "main" of the repository of the plugins, its latest version as [LAY-6](../../../../development-methodology/specs/layers.md#rules) says
      And that script reads the reference commit of each code repository, and runs the acceptance tests and records them, as ACU-34 and ACU-35 say

    Scenario: No code repository holds a workflow or a credential of the acceptance repository
      Given the continuous integration of the acceptance repository is enabled (ACU-76)
      And the user approved the plan for the project "billing", with the owner "acme" and the components "api" and "web"
      When the project is created
      Then the skill writes no file under ".github/workflows/" of "billing-code-api" or of "billing-code-web"
      And the message of ORC-6 asks for no secret in a repository of layer 4, so that no repository of layer 4 holds a credential of "billing-acceptance" (ACU-13, level 3)

    Scenario: The code of layer 4 runs without a credential that can write the acceptance repository
      Given the project "billing" was created
      When the workflow ".github/workflows/acceptance.yml" of "billing-acceptance" runs
      Then each "build" of "product", and the acceptance tests, run in a job whose token can only read "billing-acceptance", and whose checkouts keep no token
      And a separate job, which runs no code of layer 4, pushes to "main" only the files "records/*.jsonl" that the first job produced (ACU-13, level 3)

    Scenario Outline: The code of layer 4 cannot change the recorded evidence
      Given "records/AU-3.jsonl" of "billing-acceptance" holds recorded lines
      When a run of ".github/workflows/acceptance.yml" produces a "records/AU-3.jsonl" in which <change>
      Then the job that pushes "records/" fails and records nothing, since what the run adds breaks <clause>

      Examples:
        | change                                                                                   | clause                                                                   |
        | a recorded line is changed or removed                                                    | ACU-35: lines are only added                                             |
        | an added line has a "kind" other than "test"                                             | ACU-35: the continuous integration writes only the lines of kind "test"  |
        | an added line has a "produced_by" other than the URL of that run                         | ACU-35: "produced_by" of a test is the URL of the run                    |
        | the added lines do not all have the same "date"                                          | ACU-34, step 6: all the lines of a run have the same "date"              |
        | the one "date" of the added lines is not later than the "date" of every recorded "test"  | ACU-34, step 3: the last recorded run is the one with the latest "date"  |

    Scenario: The token of the code repositories is never in the environment of the run
      Given the project "billing" was created
      When the workflow ".github/workflows/acceptance.yml" of "billing-acceptance" runs
      Then only the step before "acceptance_ci.py" has the secret "CODE_READ_TOKEN" in its environment, and it writes it to a file outside the acceptance repository
      And the step that runs "acceptance_ci.py" passes that file with "--token-file" and has no "CODE_READ_TOKEN" in its environment, as ACU-34 says

    Scenario: The workflow checks out the whole history of the acceptance repository
      Given the last recorded run of "billing-acceptance" has an "acceptance_commit" that is not HEAD, because a commit of "records/" followed it
      When the workflow ".github/workflows/acceptance.yml" runs on its schedule, and no reference commit and no file outside "records/" changed
      Then step 3 of ACU-34 finds that commit in the checkout, and the run adds no line to "records/"

    Scenario: The acceptance workflow before there is code to test
      Given "acceptance.json" of "billing-acceptance" has "test_command" an empty string, as CRP-2 writes it
      When the workflow ".github/workflows/acceptance.yml" runs
      Then the run succeeds
      And it adds no line to "records/"

    Scenario: The skill creates no secret
      When the project "billing" is created
      Then the skill creates no token and no secret on GitHub

  Rule: CRP-3 While the continuous integration of the acceptance repository is deferred (ACU-76), the skill writes no workflow, and asks for the token of the evidence runs of the orchestrator instead of the secret of CRP-1
    Rationale: while the continuous integration is deferred, the orchestrator makes every evidence run (ACU-76), and it reads the code repositories only with a token that can only read them (WFO-9); a workflow that ran beside it would make evidence runs that nobody started from the orchestration repository.

    Scenario: No workflow while the continuous integration is deferred
      Given the continuous integration of the acceptance repository is deferred (ACU-76)
      When the project "billing" is created
      Then the skill writes no file under ".github/workflows/" of any repository of the project
      And it shows neither the message of the secret nor the message of the scheduled workflow of ORC-6

    Scenario Outline: The token that the evidence runs of the orchestrator need
      Given the continuous integration of the acceptance repository is deferred (ACU-76)
      And the project "billing" was created, with the owner "acme" and <components>
      Then the skill shows, after the URLs of ORC-6:
        """
        The evidence runs of billing-orchestration need one token, which I did not create. Create on GitHub a fine-grained token with read-only access to the contents of <code repositories>, and to no other repository, and save it, alone, in the file ~/.config/indra-software-factory/acme/billing-orchestration/code-read-token, readable only by you.
        """

      Examples:
        | components                                 | code repositories                                      |
        | no component                               | billing-code                                           |
        | the components "api" and "web"             | billing-code-api and billing-code-web                  |

  Rule: CRP-2 The skill writes the acceptance.json of the acceptance repository with the default done profile that the user chose

    Scenario: The user chose the profile "product"
      Given the user approved the plan for the project "billing", with the default done profile "product"
      When the project is created
      Then "billing-acceptance" holds "acceptance.json" with "default_done_profile" "product", "last_area_id", "last_unit_id" and "last_scenario_id" 0, "test_command" an empty string and "product" an empty object (ACU-6)

  Rule: ORC-19 A creation that fails halfway removes nothing and reports what exists

    Scenario: GitHub refuses a repository
      Given the user approved the plan for the project "billing"
      And the repositories "billing-drafts", "billing-specs", "billing-norms" and "billing-acceptance" were created
      When GitHub refuses to create "billing-code"
      Then the skill removes nothing
      And it stops
      And it reports which repositories and local folders exist, and the error that GitHub gave

  Rule: ORC-6 The skill reports where the project is, how to open it, and the credential that the evidence runs of the acceptance tests need: the secret of the workflow of the acceptance repository (CRP-1), or the token of the orchestrator (CRP-3)

    Scenario: The project was created
      Given the project "billing" was created
      Then the skill shows the URLs of every repository of the project
      And it says to open each repository alone, in its own editor window

    Scenario Outline: The secret that the workflow of CRP-1 needs
      Given the continuous integration of the acceptance repository is enabled (ACU-76)
      And the project "billing" was created, with <components>
      Then the skill shows:
        """
        The workflow of billing-acceptance needs one secret, which I did not create. Add it on GitHub, in billing-acceptance, Settings > Secrets and variables > Actions:
        - CODE_READ_TOKEN: a fine-grained token with read-only access to the contents of <code repositories>, and to no other repository.
        """

      Examples:
        | components                                 | code repositories                                      |
        | no component                               | billing-code                                           |
        | the components "api" and "web"             | billing-code-api and billing-code-web                  |
        | the components "api", "web" and "mobile"   | billing-code-api, billing-code-web and billing-code-mobile |

    Scenario: The repositories of the project are public
      Given the continuous integration of the acceptance repository is enabled (ACU-76)
      And the project "billing" was created, with the visibility "public"
      Then after the message of the secret the skill shows:
        """
        billing-acceptance is public: GitHub disables its scheduled workflow after 60 days without activity in billing-acceptance, and a push to a code repository is not activity there. When that happens, the acceptance tests stop running and record nothing; enable the workflow again in billing-acceptance, Actions > acceptance.
        """

    Scenario: The repositories of the project are private
      Given the continuous integration of the acceptance repository is enabled (ACU-76)
      And the project "billing" was created, with the visibility "private"
      Then the skill shows no message about the scheduled workflow being disabled
```

Rationale of the scenario "A rule "deny" names the folder of the other repository at any depth": the project folder of each person is written nowhere (ORC-20), and a rule of Claude Code matches only the files under its anchor, so the rule is anchored at the root of the file system.
